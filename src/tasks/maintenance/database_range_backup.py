import logging
import time
import traceback
from datetime import datetime
from typing import cast

from celery import Task, shared_task
from src.common.celery import update_task_state
from src.constants import FILLER_UUID4
from src.core import get_backup_db, get_db
from src.core.s3_storage import ObjectStorage
from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.schemas import BackupCreate, BackupSchema, DateRangeRequest
from src.services import BackupService
from src.workflows import RangedBackupWorkflow


@shared_task(bind=True)
def database_ranged_backup(
    self: Task, trigger: str, start_date: str, end_date: str, *args, **kwargs
):
    db_gen = get_db()
    db = next(db_gen)

    backup_db_gen = get_backup_db()
    backup_db = next(backup_db_gen)

    start_time = time.perf_counter()

    backup_data = BackupCreate(
        celery_id=cast(str, self.request.id),
        trigger_method=BackupTriggerMethod(trigger),
        status=BackupStatus.RUNNING,
        backup_type=BackupType.RANGED,
    )

    try:
        update_task_state(self, db, metadata={"stage": "Initialising Backup Task"})

        date_range = DateRangeRequest(
            min_date=datetime.strptime(start_date, "%Y-%m-%d"),
            max_date=datetime.strptime(end_date, "%Y-%m-%d"),
        )

        service = BackupService(db=db, backup_db=backup_db)
        backup_record = service.create(backup_data)

    except Exception as e:
        backup_db_gen.close()
        db_gen.close()

        logging.error("Failure to create a backup record")
        logging.error(e)

        return BackupSchema.model_validate(
            {
                "id": FILLER_UUID4,
                "status": BackupStatus.FAILURE,
                "error_message": str(e),
                "error_traceback": traceback.format_exc(),
                **backup_data.model_dump(mode="json", exclude={"status"}),
            }
        ).model_dump(mode="json")

    workflow: RangedBackupWorkflow | None = None

    try:
        s3_storage = ObjectStorage()
        workflow = RangedBackupWorkflow(
            db=db,
            backup_db=backup_db,
            backup_record=backup_record,
            object_storage=s3_storage,
            date_range=date_range,
        )

        update_task_state(self, db, metadata={"stage": "Creating Logical Backup"})
        workflow.create_ranged_backup()

        # TODO: files backup when images are implemented
        # update_task_state(self, db, metadata={"stage": "Creating Object Storage Backups"})

        update_task_state(self, db, metadata={"stage": "Compiling Metadata"})
        workflow.generate_metadata(BackupType.RANGED)

        update_task_state(self, db, metadata={"stage": "Packaging Backup"})
        workflow.zip_all_backup_files()

        update_task_state(self, db, metadata={"stage": "Saving Packaged Backup"})
        workflow.upload_zip_to_object_storage()
        workflow.record_backup_into_database()

        update_task_state(self, db, metadata={"stage": "Finalising Backup Task"})
        end_time = time.perf_counter()

        backup_record.duration = end_time - start_time
        backup_record.status = BackupStatus.SUCCESS

        backup_db.commit()

        return BackupSchema.model_validate(backup_record).model_dump(mode="json")

    except Exception as e:
        db.rollback()
        backup_db.rollback()

        end_time = time.perf_counter()
        logging.info("Timer stopped on failure")

        backup_record.duration = end_time - start_time
        backup_record.status = BackupStatus.FAILURE
        backup_record.error_message = str(e)
        backup_record.error_traceback = traceback.format_exc()

        logging.error(backup_record.error_traceback)
        logging.error(backup_record.error_message)

        backup_db.commit()

    finally:
        if workflow:
            workflow.cleanup()

        backup_db_gen.close()
        db_gen.close()
