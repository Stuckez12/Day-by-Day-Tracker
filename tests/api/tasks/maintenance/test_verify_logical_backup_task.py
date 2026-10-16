import subprocess
import uuid

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupType, TaskStatus
from src.models import BackupModel, TaskModel
from src.schemas import VerifiedBackupResultSchema
from src.tasks import verify_logical_backup
from src.workflows import LogicalBackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestVerifyBackupTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)

        task: AsyncResult = verify_logical_backup.apply_async(
            kwargs={"backup_id": test_logical_backup_zip_stored.id},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is True
        assert backup.backup_type == BackupType.LOGICAL
        assert backup.error_message is None
        assert backup.error_traceback is None

    def test_no_backup_record(
        self,
        celery_worker: None,
        test_task_1: TaskModel,
    ):
        task: AsyncResult = verify_logical_backup.apply_async(
            kwargs={"backup_id": uuid.uuid4()}, task_id=str(test_task_1.task_id)
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.backup_type is None
        assert backup.error_message == "Backup not found"
        assert backup.error_traceback is not None

    def test_backup_has_no_metadata(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)

        test_logical_backup_zip_stored.meta = None
        test_backup_session.commit()

        task: AsyncResult = verify_logical_backup.apply_async(
            kwargs={"backup_id": test_logical_backup_zip_stored.id},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.backup_type is None
        assert backup.error_message == "Backup has no metadata"
        assert backup.error_traceback is not None

    def test_backup_workflow_fails(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)
        mocker.patch.object(
            LogicalBackupWorkflow, "retrieve_zip_file", side_effect=RuntimeError
        )

        task: AsyncResult = verify_logical_backup.apply_async(
            kwargs={"backup_id": test_logical_backup_zip_stored.id},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.backup_type == test_logical_backup_zip_stored.backup_type
        assert backup.error_message is not None
        assert backup.error_traceback is not None

    def test_task_cancelled(
        self,
        celery_worker: None,
        test_session: Session,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        test_task_1.status = TaskStatus.CANCELLED
        test_session.commit()

        task: AsyncResult = verify_logical_backup.apply_async(
            kwargs={"backup_id": test_logical_backup_zip_stored.id},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.backup_type == test_logical_backup_zip_stored.backup_type
        assert backup.error_message is not None
        assert backup.error_traceback is not None
