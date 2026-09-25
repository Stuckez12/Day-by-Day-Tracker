import subprocess
import uuid

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupType
from src.models import BackupModel
from src.schemas import VerifiedBackupResultSchema
from src.tasks import verify_backup
from src.workflows import BackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestVerifyBackupTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_zip_stored: BackupModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)

        task: AsyncResult = verify_backup.delay(backup_id=test_backup_zip_stored.id)
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is True
        assert backup.backup_type == BackupType.LOGICAL
        assert backup.error_message is None
        assert backup.error_traceback is None

    def test_no_backup_record(self, celery_worker: None):
        task: AsyncResult = verify_backup.delay(backup_id=uuid.uuid4())
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
        test_backup_zip_stored: BackupModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)

        test_backup_zip_stored.meta = None
        test_backup_session.commit()

        task: AsyncResult = verify_backup.delay(backup_id=test_backup_zip_stored.id)
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.backup_type is None
        assert backup.error_message == "Backup has no metadata"
        assert backup.error_traceback is not None

    def test_backup_workflow_fails(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_zip_stored: BackupModel,
    ):
        mocker.patch.object(subprocess, "run", return_value=None)
        mocker.patch.object(
            BackupWorkflow, "retrieve_zip_file", side_effect=RuntimeError
        )

        task: AsyncResult = verify_backup.delay(backup_id=test_backup_zip_stored.id)
        backup = VerifiedBackupResultSchema.model_validate(task.result)
        assert backup.verified is False
        assert backup.backup_type == test_backup_zip_stored.backup_type
        assert backup.error_message is not None
        assert backup.error_traceback is not None
