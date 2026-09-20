import logging
import time
from typing import cast

from celery import Task, shared_task
from src.common.celery import update_task_state
from src.constants import FILLER_UUID4
from src.core import get_backup_db, get_db
from src.core.s3_storage import ObjectStorage
from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.schemas import BackupCreate, BackupSchema
from src.services import BackupService
from src.settings import app_config
from src.workflows import BackupWorkflow


@shared_task(bind=True)
def database_logical_backup_old(self: Task, trigger: str, *args, **kwargs) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    backup_db_gen = get_backup_db()
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
        zip_file = service.zip_folder(
            zip_destination=zip_destination,
            files=[backup_file, checksum_file, metadata_file],
        )

        end = time.perf_counter()
        logging.info("Timer stopped on success")

        logging.info("State: Finishing")
        update_task_state(self, db, metadata={"stage": "Finishing"})

        service.create_metadata_record(metadata_schema, zip_file, zip_destination)

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


@shared_task(bind=True)
def database_logical_backup(self: Task, trigger: str, *args, **kwargs):
    db_gen = get_db()
    db = next(db_gen)

    backup_db_gen = get_backup_db()
    backup_db = next(backup_db_gen)

    start = time.perf_counter()

    backup_data = BackupCreate(
        celery_id=cast(str, self.request.id),
        trigger_method=BackupTriggerMethod(trigger),
        status=BackupStatus.RUNNING,
        backup_type=BackupType.LOGICAL,
    )

    try:
        update_task_state(self, db, metadata={"stage": "Initialising Backup Task"})
        service = BackupService(db=db, backup_db=backup_db)
        backup_record = service.create(backup_data)

    except:
        backup_db_gen.close()
        db_gen.close()

        return BackupSchema.model_validate(
            {
                "id": FILLER_UUID4,
                "status": BackupStatus.FAILURE,
                **backup_data.model_dump(mode="json", exclude={"status"}),
            }
        ).model_dump(mode="json")

    try:
        s3_storage = ObjectStorage()
        workflow = BackupWorkflow(
            db=db,
            backup_db=backup_db,
            backup_record=backup_record,
            object_storage=s3_storage,
        )

        update_task_state(self, db, metadata={"stage": "Creating Logical Backup"})
        workflow.create_logical_database_backup()

        update_task_state(
            self, db, metadata={"stage": "Verifying Generated Backup File"}
        )
        workflow.verify_backup_file()

        # TODO: files backup when images are implemented
        # update_task_state(self, db, metadata={"stage": "Creating Object Storage Backups"})~

        update_task_state(self, db, metadata={"stage": "Compiling Metadata"})
        workflow.generate_metadata(BackupType.LOGICAL)

        update_task_state(self, db, metadata={"stage": "Packaging Backup"})
        workflow.zip_all_backup_files()

        update_task_state(self, db, metadata={"stage": "Saving Packaged Backup"})
        workflow.upload_zip_to_object_storage()
        workflow.record_backup_into_database()

        update_task_state(self, db, metadata={"stage": "Finalising Backup Task"})
        end = time.perf_counter()

        backup_record.duration = end - start
        backup_record.status = BackupStatus.UPLOADED

        backup_db.commit()

        return BackupSchema.model_validate(backup_record).model_dump(mode="json")

    except Exception as e:
        db.rollback()
        backup_db.rollback()

        end = time.perf_counter()
        logging.info("Timer stopped on failure")

        backup_record.duration = end - start
        backup_record.status = BackupStatus.FAILURE
        backup_record.error_message = f"{type(e).__name__}: {e}"
        backup_record.error_traceback = str(e)

        logging.error(backup_record.error_traceback)
        logging.error(backup_record.error_message)

        backup_db.commit()

        return BackupSchema.model_validate(backup_record).model_dump(mode="json")

    finally:
        backup_db_gen.close()
        db_gen.close()
