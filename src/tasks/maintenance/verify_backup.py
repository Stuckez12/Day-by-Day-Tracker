import logging
import traceback
from typing import cast
from uuid import UUID

from sqlalchemy.exc import NoResultFound

from celery import Task, shared_task
from src.common.celery import update_task_state
from src.core import get_backup_db, get_db
from src.core.s3_storage.service import ObjectStorage
from src.schemas.backup import VerifiedBackupResultSchema
from src.services import BackupService
from src.workflows.backup import BackupWorkflow


@shared_task(bind=True)
def verify_backup(self: Task, backup_id: UUID, *args, **kwargs) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    backup_db_gen = get_backup_db()
    backup_db = next(backup_db_gen)

    celery_id = cast(UUID, self.request.id)

    try:
        update_task_state(
            self, db, metadata={"stage": "Initialising Verification Task"}
        )
        service = BackupService(db=db, backup_db=backup_db)
        backup = service.get_by_backup_id(backup_id)

        if backup.meta is None:
            raise ValueError("Backup has no metadata")

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

    except ValueError as e:
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
        workflow.retrieve_zip_file()

        update_task_state(
            self, db, metadata={"stage": "Validating Backup Files' Integrity"}
        )
        workflow.retrieve_metadata_from_file()
        workflow.validate_metadata_checksums()

        update_task_state(self, db, metadata={"stage": "Validating Backup Restoration"})
        workflow.verify_backup_file()

        update_task_state(self, db, metadata={"stage": "Finalising Verification Task"})
        workflow.update_verification_metadata_record()

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
                workflow.update_verification_metadata_record(verified=False)

                backup_db.commit()

            except Exception:
                logging.exception("Failed to record backup verification failure")

        return VerifiedBackupResultSchema(
            id=backup_id,
            celery_id=celery_id,
            verified=False,
            error_message="Backup verification raised an unexpected error",
            error_traceback=traceback.format_exc(),
        ).model_dump(mode="json")

    finally:
        if workflow:
            workflow.cleanup()

        backup_db_gen.close()
        db_gen.close()
