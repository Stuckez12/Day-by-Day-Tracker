import logging
import traceback
from typing import cast
from uuid import UUID

from sqlalchemy.exc import NoResultFound

import src.core as core
from celery import Task, shared_task
from src.common.celery import update_task_state
from src.core.s3_storage import ObjectStorage
from src.enums import BackupType
from src.schemas import DateRangeRequest, VerifiedBackupResultSchema
from src.services import BackupService, TaskService
from src.workflows import RangedBackupWorkflow


@shared_task(bind=True)
def verify_ranged_backup(self: Task, backup_id: UUID, *args, **kwargs) -> dict:
    db_gen = core.get_db()
    db = next(db_gen)

    backup_db_gen = core.get_backup_db()
    backup_db = next(backup_db_gen)

    celery_id = cast(UUID, self.request.id)

    try:
        update_task_state(
            self, db, metadata={"stage": "Initialising Verification Task"}
        )
        service = BackupService(db=db, backup_db=backup_db)
        backup = service.get_by_backup_id(backup_id)

        if backup.backup_type not in [BackupType.RANGED_DAY, BackupType.RANGED_WEEK]:
            raise ValueError("Backup is not of type RANGED")

        if backup.meta is None:
            raise ValueError("Backup has no metadata")

        backup.set_verifying(celery_id)
        backup_db.commit()

    except NoResultFound as e:
        backup_db_gen.close()
        db_gen.close()

        logging.error("Failure to retrieve backup record")
        logging.error(e)

        return VerifiedBackupResultSchema(
            id=backup_id,
            celery_id=celery_id,
            verified=False,
            error_message="Backup not found",
            error_traceback=traceback.format_exc(),
        ).model_dump(mode="json")

    except Exception as e:
        backup_db_gen.close()
        db_gen.close()

        logging.error(e)

        return VerifiedBackupResultSchema(
            id=backup_id,
            celery_id=celery_id,
            verified=False,
            error_message=str(e),
            error_traceback=traceback.format_exc(),
        ).model_dump(mode="json")

    workflow: RangedBackupWorkflow | None = None

    try:
        s3_storage = ObjectStorage()
        task_service = TaskService(db)
        workflow = RangedBackupWorkflow(
            db=db,
            backup_db=backup_db,
            backup_record=backup,
            object_storage=s3_storage,
            task_service=task_service,
            date_range=DateRangeRequest(
                min_date=backup.meta.date_range_start.date(),
                max_date=backup.meta.date_range_end.date(),
            ),
        )

        update_task_state(self, db, metadata={"stage": "Retrieving Backup ZIP File"})
        workflow.retrieve_zip_file()

        update_task_state(
            self, db, metadata={"stage": "Validating Backup Files' Integrity"}
        )
        workflow.retrieve_metadata_from_file()
        workflow.validate_metadata_checksums()

        update_task_state(self, db, metadata={"stage": "Finalising Verification Task"})
        workflow.update_verification_metadata_record()

        backup.set_successful()
        backup_db.commit()

        return VerifiedBackupResultSchema(
            id=backup_id,
            celery_id=celery_id,
            verified=backup.meta.verified,
            backup_type=backup.backup_type,
        ).model_dump(mode="json")

    except Exception:
        db.rollback()
        backup_db.rollback()

        if workflow:
            try:
                workflow.update_verification_metadata_record(
                    verified=False, check_if_task_cancelled=False
                )

            except Exception:
                logging.exception("Failed to record backup verification failure")

        backup.set_failed()
        backup_db.commit()

        return VerifiedBackupResultSchema(
            id=backup_id,
            celery_id=celery_id,
            backup_type=backup.backup_type,
            verified=False,
            error_message="Backup verification raised an unexpected error",
            error_traceback=traceback.format_exc(),
        ).model_dump(mode="json")

    finally:
        if workflow:
            workflow.cleanup()

        backup_db_gen.close()
        db_gen.close()
