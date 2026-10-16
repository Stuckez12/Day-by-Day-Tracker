import subprocess

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupType, TaskStatus
from src.models import BackupModel, TaskModel
from src.schemas import VerifiedBackupResultSchema
from src.tasks import uploaded_backup_record_creation
from src.workflows import LogicalBackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestUploadBackupRecordCreationTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)
        assert test_logical_backup_zip_stored.meta

        task: AsyncResult = uploaded_backup_record_creation.apply_async(
            kwargs={"new_backup_file": test_logical_backup_zip_stored.meta.zip_path},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)

        try:
            assert backup.verified is True
            assert backup.backup_type == BackupType.UPLOADED
            assert backup.error_message is None
            assert backup.error_traceback is None

        finally:
            record = test_backup_session.get(BackupModel, backup.id)

            if record is not None:
                test_backup_session.delete(record)
                test_backup_session.commit()

    def test_backup_workflow_fails(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)
        mocker.patch.object(
            LogicalBackupWorkflow,
            "retrieve_downloaded_zip_file",
            side_effect=RuntimeError,
        )
        assert test_logical_backup_zip_stored.meta

        task: AsyncResult = uploaded_backup_record_creation.apply_async(
            kwargs={"new_backup_file": test_logical_backup_zip_stored.meta.zip_path},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)

        try:
            assert backup.verified is False
            assert backup.error_message is not None
            assert backup.error_traceback is not None

        finally:
            record = test_backup_session.get(BackupModel, backup.id)

            if record is not None:
                test_backup_session.delete(record)
                test_backup_session.commit()

    def test_task_cancelled(
        self,
        celery_worker: None,
        test_session: Session,
        test_backup_session: Session,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
    ):
        test_task_1.status = TaskStatus.CANCELLED
        test_session.commit()

        assert test_logical_backup_zip_stored.meta

        task: AsyncResult = uploaded_backup_record_creation.apply_async(
            kwargs={"new_backup_file": test_logical_backup_zip_stored.meta.zip_path},
            task_id=str(test_task_1.task_id),
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)

        try:
            assert backup.verified is False
            assert backup.error_message is not None
            assert backup.error_traceback is not None

        finally:
            record = test_backup_session.get(BackupModel, backup.id)

            if record is not None:
                test_backup_session.delete(record)
                test_backup_session.commit()
