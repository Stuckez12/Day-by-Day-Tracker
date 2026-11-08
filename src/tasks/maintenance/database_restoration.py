from typing import cast
from uuid import UUID

from celery import Task, shared_task
from sqlalchemy.exc import NoResultFound

import src.core as core
from src.core import LinkedNode
from src.core.app_settings import get_configurable_application_settings
from src.core.database.restore_db import application_is_configured_to_be_restored
from src.models import BackupModel
from src.schemas import DetailSchema
from src.services import BackupService


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

    # Verify backup and the chain
    try:
        service = BackupService(db, backup_db)
        backup = service.get_by_backup_id(final_backup_id)

        backup_chain = service.get_backup_chain(backup)

        def convert_to_ids(node: LinkedNode):
            item: BackupModel = node.item
            new_item = {"model_id": item.id, "parent_id": item.parent_backup_id}
            node.item = new_item

            return node

        backup_chain.modify_all_node_items(mod_func=convert_to_ids)

        print(backup_chain)

    except NoResultFound:
        pass

    except Exception:
        pass

    finally:
        backup_db_gen.close()
        db_gen.close()

    # restoration pipeline
    try:
        pass

    except Exception:
        pass
