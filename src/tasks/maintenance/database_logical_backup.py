import logging
import time
from typing import cast

import src.common as common
from celery import Task, shared_task
from src.common.celery import update_task_state
from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.schemas import BackupCreate, BackupSchema
from src.services import BackupService
from src.settings import app_config


@shared_task(bind=True)
def database_logical_backup(self: Task, trigger: str, *args, **kwargs) -> dict:
    db_gen = common.get_db()
    db = next(db_gen)

    backup_db_gen = common.get_backup_db()
    backup_db = next(backup_db_gen)

    service = BackupService(db=db, backup_db=backup_db)

    logging.info("Starting timer")
    start = time.perf_counter()

    backup_data = BackupCreate(
        celery_id=cast(str, self.request.id),
        trigger_method=BackupTriggerMethod(trigger),
        status=BackupStatus.RUNNING,
        backup_type=BackupType.LOGICAL,
    )
    backup = service.create(backup_data)

    temp_folder_path = service.create_folder(service.temp_file_path)

    try:
        logging.info("State: Creating Backup")
        update_task_state(self, db, metadata={"stage": "Creating Backup"})
        backup_file = service.create_logical_backup()

        logging.info("State: Verifying Backup")
        update_task_state(self, db, metadata={"stage": "Verifying Backup"})
        service.verify_backup_restoration(backup_file)

        logging.info("State: Compiling Backup")
        update_task_state(self, db, metadata={"stage": "Compiling Backup"})
        checksum_file = service.generate_checksum_file(backup_file)

        logging.debug("Metadata creation")
        metadata_schema = service.create_metadata(backup, backup_file, checksum_file)
        metadata_file = service.create_metadata_file(metadata_schema)

        logging.info("Zipping up all the files")
        zip_destination = f"{app_config.BACKUP_PATH}/{metadata_schema.created_at.strftime('%Y%m%d%H%M%S')}-tracker-backup.zip"
        service.zip_folder(
            zip_destination=zip_destination,
            files=[backup_file, checksum_file, metadata_file],
        )

        end = time.perf_counter()
        logging.info("Timer stopped on success")

        logging.info("State: Finishing")
        update_task_state(self, db, metadata={"stage": "Finishing"})

        service.create_metadata_record(metadata_schema, zip_destination)

        backup.duration = end - start
        backup.status = BackupStatus.SUCCESS

        backup_db.commit()

        return BackupSchema.model_validate(backup).model_dump(mode="json")

    except Exception as e:
        db.rollback()
        backup_db.rollback()

        end = time.perf_counter()
        logging.info("Timer stopped on failure")

        backup.duration = end - start
        backup.status = BackupStatus.FAILURE
        backup.error_message = f"{type(e).__name__}: {e}"
        backup.error_traceback = str(e)

        backup_db.commit()

        return BackupSchema.model_validate(backup).model_dump(mode="json")

    finally:
        service.delete_folder(temp_folder_path)

        backup_db_gen.close()
        db_gen.close()
