import subprocess

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.enums import BackupType
from src.models import BackupModel
from src.schemas import VerifiedBackupResultSchema
from src.tasks import uploaded_backup_record_creation
from src.workflows import BackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestUploadBackupRecordCreationTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_backup_zip_stored: BackupModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)
        assert test_backup_zip_stored.meta

        task: AsyncResult = uploaded_backup_record_creation.delay(
            new_backup_file=test_backup_zip_stored.meta.zip_path
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is True
        assert backup.backup_type == BackupType.UPLOADED
        assert backup.error_message is None
        assert backup.error_traceback is None

        test_backup_session.execute(
            delete(BackupModel).where(BackupModel.id == backup.id)
        )
        test_backup_session.commit()

    def test_backup_workflow_fails(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_backup_zip_stored: BackupModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)
        mocker.patch.object(
            BackupWorkflow, "retrieve_downloaded_zip_file", side_effect=RuntimeError
        )
        assert test_backup_zip_stored.meta

        task: AsyncResult = uploaded_backup_record_creation.delay(
            new_backup_file=test_backup_zip_stored.meta.zip_path
        )
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.error_message is not None
        assert backup.error_traceback is not None

        test_backup_session.execute(
            delete(BackupModel).where(BackupModel.id == backup.id)
        )
        test_backup_session.commit()
