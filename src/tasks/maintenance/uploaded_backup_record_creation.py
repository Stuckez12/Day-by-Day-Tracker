import logging
import time
import traceback
from typing import cast
from uuid import UUID

from celery import Task, shared_task
from src.common.celery import update_task_state
from src.constants import FILLER_UUID4
from src.core import get_backup_db, get_db
from src.core.s3_storage import ObjectStorage
from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.schemas import BackupCreate, VerifiedBackupResultSchema
from src.services import BackupService
from src.workflows import BackupWorkflow


# NOTE: Might not need this route as if im doing the uploading in the api the
# verify task can do all the work after (this wpould more or less be a duplicate)
@shared_task(bind=True)
def uploaded_backup_record_creation(self: Task, new_backup_file: str, *args, **kwargs):
    db_gen = get_db()
    db = next(db_gen)

    backup_db_gen = get_backup_db()
    backup_db = next(backup_db_gen)

    celery_id = cast(UUID, self.request.id)

    start = time.perf_counter()

    try:
        update_task_state(self, db, metadata={"stage": "Initialising Uploading Task"})
        backup_data = BackupCreate(
            celery_id=str(celery_id),
            trigger_method=BackupTriggerMethod.MANUAL,
            status=BackupStatus.RUNNING,
            backup_type=BackupType.UPLOADED,
        )

        service = BackupService(db=db, backup_db=backup_db)
        backup = service.create(backup_data)

    except Exception as e:
        backup_db_gen.close()
        db_gen.close()

        logging.error(e)

        return VerifiedBackupResultSchema(
            id=cast(UUID, FILLER_UUID4),
            celery_id=celery_id,
            verified=False,
            error_message=str(e),
            error_traceback=traceback.format_exc(),
        ).model_dump(mode="json")

    workflow: BackupWorkflow | None = None

    try:
        s3_storage = ObjectStorage()
        workflow = BackupWorkflow(
            db=db,
            backup_db=backup_db,
            backup_record=backup,
            object_storage=s3_storage,
        )

        update_task_state(self, db, metadata={"stage": "Retrieving Backup ZIP File"})
        workflow.retrieve_downloaded_zip_file(new_backup_file)

        update_task_state(
            self, db, metadata={"stage": "Validating Backup Files' Integrity"}
        )
        workflow.retrieve_metadata_from_file()
        workflow.validate_metadata_checksums()

        update_task_state(self, db, metadata={"stage": "Validating Backup Restoration"})
        workflow.verify_backup_file()

        update_task_state(self, db, metadata={"stage": "Recording Packaged Backup"})
        workflow.record_backup_into_database()

        update_task_state(self, db, metadata={"stage": "Finalising Uploading Task"})
        end = time.perf_counter()

        backup.duration = end - start
        backup.status = BackupStatus.UPLOADED

        backup_db.commit()
        backup_db.refresh(backup)

        if backup.meta is None:
            raise RuntimeError(
                "Backup record has no metadata after upload verification"
            )

        return VerifiedBackupResultSchema(
            id=backup.id,
            celery_id=celery_id,
            verified=backup.meta.verified,
            backup_type=backup.backup_type,
        ).model_dump(mode="json")

    except Exception as e:
        db.rollback()
        backup_db.rollback()

        end = time.perf_counter()
        logging.info("Timer stopped on failure")

        backup.duration = end - start
        backup.status = BackupStatus.FAILURE
        backup.error_message = str(e)
        backup.error_traceback = traceback.format_exc()

        logging.error(backup.error_traceback)
        logging.error(backup.error_message)

        backup_db.commit()

        return VerifiedBackupResultSchema(
            id=backup.id,
            celery_id=celery_id,
            verified=False,
            error_message="Backup uploading raised an unexpected error",
            error_traceback=traceback.format_exc(),
        ).model_dump(mode="json")

    finally:
        if workflow:
            workflow.cleanup()

        backup_db_gen.close()
        db_gen.close()
