import logging
from pathlib import Path
from typing import cast
from uuid import UUID

from celery import Task, shared_task
from sqlalchemy.exc import NoResultFound
from sqlalchemy_utils import database_exists, drop_database

import src.core as core
from src.core import LinkedNode
from src.core.app_settings import get_configurable_application_settings
from src.core.database.restore_db import application_is_configured_to_be_restored
from src.core.s3_storage import ObjectStorage
from src.models import BackupModel
from src.schemas import BackupLink, DetailSchema
from src.services import BackupService
from src.settings import app_config
from src.workflows import BackupRestorationWorkflow


TEMP_RESTORATION_PATH = Path(app_config.TEMPORARY_PATH + "/backup-restoration")


@shared_task(bind=True)
def database_restoration(self: Task, *args, **kwargs) -> dict:
    configurable_settings = get_configurable_application_settings()

    if not application_is_configured_to_be_restored(configurable_settings):
        return DetailSchema(
            detail="There is no backup assigned for the application to restore to"
        ).model_dump(mode="json")

    db_gen = core.get_db()
    db = next(db_gen)

    backup_db_gen = core.get_backup_db()
    backup_db = next(backup_db_gen)

    final_backup_id = cast(UUID, configurable_settings.RESTORE_DATABASE_TO_BACKUP_ID)
    final_backup_id = UUID("b0c37212-0bfd-492b-8716-11511b501b01")

    object_storage = ObjectStorage()

    workflow = BackupRestorationWorkflow()

    # Verify backup and the chain
    try:
        # Just in case, clean up the restoration folder
        workflow.cleanup_folder(TEMP_RESTORATION_PATH)
        TEMP_RESTORATION_PATH.mkdir(exist_ok=True)

        service = BackupService(db, backup_db)
        backup = service.get_by_backup_id(final_backup_id)

        backup_chain = service.get_backup_chain(backup)

        mapped_file_paths: dict[UUID, Path] = {}

        # Locally download all stored files onto tmp disk for fast access
        # Can become a problem if the files overall become larger
        # than Pi Memory (although unlikely)
        for node in backup_chain.linked_list.values():
            file_path = service.retrieve_zip_file(
                node.item, object_storage, TEMP_RESTORATION_PATH
            )

            mapped_file_paths[node.item.id] = file_path

        # Modify chain to only contain required data
        def convert_to_ids(node: LinkedNode):
            item: BackupModel = node.item

            new_item = BackupLink(
                model_id=item.id,
                parent_id=item.parent_backup_id,
                backup_type=item.backup_type,
                zip_file_path=mapped_file_paths[item.id],
            )
            node.item = new_item

            return node

        backup_chain.modify_all_node_items(mod_func=convert_to_ids)

    except NoResultFound:
        workflow.cleanup_folder(TEMP_RESTORATION_PATH)

        raise ValueError("Backup provided does not exist")

    except Exception:
        workflow.cleanup_folder(TEMP_RESTORATION_PATH)

        raise

    finally:
        backup_db_gen.close()
        db_gen.close()

    # Restore and validate in isolation while production remains available.
    switched = False
    try:
        workflow.use_chain(backup_chain)
        workflow.restore_new_database_to_logical_backup()
        workflow.fully_restore_logical_database_to_latest_ranged_backup()

        workflow.validate_restored_database()

        workflow.switch_restored_database_into_service()

        switched = True

        return DetailSchema(detail="Database restoration completed").model_dump(
            mode="json"
        )
    except Exception:
        logging.exception("Database restoration failed")

        raise

    finally:
        try:
            # A failed restore may leave an empty or partially populated database.
            # Only remove the staging database owned by this attempt.
            if (
                not switched
                and workflow.restoration_database_created
                and database_exists(app_config.restoration_db_url)
            ):
                drop_database(app_config.restoration_db_url)

        except Exception:
            logging.exception("Unable to clean up the restoration database")

        workflow.cleanup_folder(TEMP_RESTORATION_PATH)
