import logging
from datetime import datetime
from uuid import UUID

import src.common as common
from celery import Task, shared_task
from src.common.celery import update_task_state
from src.enums.backup.status import BackupStatus
from src.schemas.backup import BackupSchema
from src.services import BackupService


@shared_task(bind=True)
def verify_backup(self: Task, backup_id: UUID, *args, **kwargs) -> dict:
    db_gen = common.get_db()
    db = next(db_gen)

    backup_db_gen = common.get_backup_db()
    backup_db = next(backup_db_gen)

    service = BackupService(db=db, backup_db=backup_db)

    temp_folder_path = service.create_folder(service.temp_restore_path)

    backup = service.get_by_backup_id(backup_id)

    try:
        if backup.meta is None:
            raise ValueError("Metadata is not attached to the backup")

        logging.info("State: Extracting Backup")
        update_task_state(self, db, metadata={"stage": "Extracting Backup"})
        service.unzip_folder(backup.meta.zip_filename)

        metadata_schema = service.get_metadata_from_backup(backup)
        backup.meta.backup_id = str(backup.id)

        logging.info("State: Verifying Checksum")
        update_task_state(self, db, metadata={"stage": "Verifying Checksum"})
        service.validate_checksum(metadata_schema)

        logging.info("State: Validating Backup")
        update_task_state(self, db, metadata={"stage": "Validating Backup"})
        backup_file = metadata_schema.get_file_type_data("backup")

        if backup_file is None:
            raise ValueError("Backup file is not present")

        service.verify_backup_restoration(
            f"{service.temp_restore_path}/{backup_file.name}"
        )

        backup.meta.verified = True

        return BackupSchema.model_validate(backup).model_dump(mode="json")

    except Exception as e:
        db.rollback()
        backup_db.rollback()

        if backup.meta is not None:
            backup.meta.verified = False

        backup.error_message = f"{type(e).__name__}: {e}"
        backup.error_traceback = str(e)

        schema = BackupSchema.model_validate(backup).model_dump(mode="json")
        schema["status"] = BackupStatus.FAILURE.value

        return schema

    finally:
        service.delete_folder(temp_folder_path)

        if backup.meta is not None:
            backup.meta.last_verified = datetime.now()
            backup_db.commit()

        backup_db_gen.close()
        db_gen.close()
