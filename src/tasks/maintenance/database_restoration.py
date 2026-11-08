from typing import cast
from uuid import UUID

from celery import Task, shared_task

import src.core as core  # noqa
from src.core.app_settings import get_configurable_application_settings
from src.core.database.restore_db import application_is_configured_to_be_restored
from src.schemas import DetailSchema


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

    # Verify backup and the chain
    try:
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
