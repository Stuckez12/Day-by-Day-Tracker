import logging
from typing import cast

import src.core as core
from celery import Task, shared_task
from src.common.celery import update_task_state
from src.enums.backup.status import BackupStatus
from src.enums.backup.trigger_method import BackupTriggerMethod
from src.enums.backup.type import BackupType
from src.schemas.backup import BackupCreate, BackupSchema
from src.services import BackupService


@shared_task(bind=True)
def uploaded_backup_record_creation(
    self: Task, new_backup_file: str, *args, **kwargs
) -> dict:
    db_gen = core.get_db()
    db = next(db_gen)

    backup_db_gen = core.get_backup_db()
    backup_db = next(backup_db_gen)

    service = BackupService(db=db, backup_db=backup_db)

    temp_folder_path = service.create_folder(service.temp_restore_path)

    backup_data = BackupCreate(
        celery_id=cast(str, self.request.id),
        trigger_method=BackupTriggerMethod.MANUAL,
        status=BackupStatus.RUNNING,
        backup_type=BackupType.LOGICAL,
    )
    backup = service.create(backup_data)

    try:
        logging.info("State: Extracting Backup")
        update_task_state(self, db, metadata={"stage": "Extracting Backup"})
        zip_path = service.unzip_folder(new_backup_file)

        metadata_schema = service.get_metadata_from_backup(backup)
        metadata_schema.backup_id = str(backup.id)

        logging.info("State: Validating Backup")
        update_task_state(self, db, metadata={"stage": "Validating Backup"})
        service.validate_checksum(metadata_schema)

        logging.info("State: Creating Backup Record")
        update_task_state(self, db, metadata={"stage": "Creating Backup Record"})
        service.create_metadata_record(metadata_schema, zip_path)

        backup.duration = 0
        backup.status = BackupStatus.UPLOADED

        backup_db.commit()

        return BackupSchema.model_validate(backup).model_dump(mode="json")

    except Exception as e:
        db.rollback()
        backup_db.rollback()

        backup.duration = 0
        backup.status = BackupStatus.FAILURE
        backup.error_message = f"{type(e).__name__}: {e}"
        backup.error_traceback = str(e)

        backup_db.commit()

        return BackupSchema.model_validate(backup).model_dump(mode="json")

    finally:
        service.delete_folder(temp_folder_path)

        backup_db_gen.close()
        db_gen.close()
