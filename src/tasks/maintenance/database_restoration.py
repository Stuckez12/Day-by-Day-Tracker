from dataclasses import dataclass
from pathlib import Path
from typing import cast
from uuid import UUID

from celery import Task, shared_task
from sqlalchemy.exc import NoResultFound

import src.core as core
from src.core import LinkedNode
from src.core.app_settings import get_configurable_application_settings
from src.core.database.restore_db import application_is_configured_to_be_restored
from src.core.s3_storage import ObjectStorage
from src.enums import BackupType
from src.models import BackupModel
from src.schemas import DetailSchema
from src.services import BackupService
from src.settings import app_config
from src.workflows import BackupRestorationWorkflow


TEMP_RESTORATION_PATH = Path(app_config.TEMPORARY_PATH + "/backup-restoration")


@dataclass(frozen=True)
class BackupLink:
    model_id: UUID
    parent_id: UUID | None
    backup_type: BackupType
    zip_file_path: Path


@shared_task(bind=True)
def database_restoration(self: Task, *args, **kwargs) -> dict:
    celery_id = cast(UUID, self.request.id)

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
        # Can become a problem if the files overall become larger than Pi Memory (although unlikely)
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

        return DetailSchema(detail="Backup provided does not exist").model_dump(
            mode="json"
        )

    except Exception:
        workflow.cleanup_folder(TEMP_RESTORATION_PATH)

        return DetailSchema(
            detail="An unknown exception while trying to retrieve the backup chain"
        ).model_dump(mode="json")

    finally:
        backup_db_gen.close()
        db_gen.close()

    # restoration pipeline
    try:
        pass

    except Exception:
        pass

    finally:
        workflow.cleanup_folder(TEMP_RESTORATION_PATH)
