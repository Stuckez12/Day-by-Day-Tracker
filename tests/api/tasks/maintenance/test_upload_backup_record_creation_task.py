import subprocess
from pathlib import Path

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupStatus
from src.models import BackupModel
from src.schemas import BackupSchema
from src.services.backup import BackupService
from src.tasks import uploaded_backup_record_creation


@pytest.mark.usefixtures("mock_task_db")
class TestUploadBackupRecordCreationTask:
    def test_success(
        self,
        shared_tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_backup_zip: Path,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(shared_tmp_path))
        mocker.patch.object(subprocess, "run", return_value=None)
        task: AsyncResult = uploaded_backup_record_creation.delay(
            new_backup_file=str(test_backup_zip)
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.UPLOADED, backup.model_dump()

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == backup.celery_id
        ).delete()
        test_backup_session.commit()

    def test_unzip_folder_step_fails(
        self,
        shared_tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_backup_zip: Path,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(shared_tmp_path))
        mocker.patch.object(
            BackupService,
            "unzip_folder",
            side_effect=ValueError("unzip_folder failed"),
        )

        task: AsyncResult = uploaded_backup_record_creation.delay(
            new_backup_file=str(test_backup_zip)
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message == "ValueError: unzip_folder failed"
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()

    def test_validate_checksum_step_fails(
        self,
        shared_tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_backup_zip: Path,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(shared_tmp_path))
        mocker.patch.object(
            BackupService,
            "validate_checksum",
            side_effect=ValueError("validate_checksum failed"),
        )

        task: AsyncResult = uploaded_backup_record_creation.delay(
            new_backup_file=str(test_backup_zip)
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message == "ValueError: validate_checksum failed"
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()
