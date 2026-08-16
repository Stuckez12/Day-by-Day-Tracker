import subprocess
from pathlib import Path

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupTriggerMethod
from src.enums.backup.status import BackupStatus
from src.models import BackupModel
from src.schemas import BackupSchema
from src.services import BackupService
from src.tasks import database_logical_backup


@pytest.mark.usefixtures("mock_task_db")
class TestDatabaseLogicalBackupTask:
    def test_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        mocker.patch.object(subprocess, "run", return_value=None)
        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        assert BackupSchema.model_validate(task.result)

        backup = BackupSchema.model_validate(task.result)
        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == backup.celery_id
        ).delete()
        test_backup_session.commit()

    def test_create_backup_step_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        mocker.patch.object(
            BackupService, "create_logical_backup", side_effect=ValueError
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message is not None
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()

    def test_verification_step_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        mocker.patch.object(
            BackupService, "verify_backup_restoration", side_effect=ValueError
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message is not None
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()

    def test_checksum_step_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        mocker.patch.object(
            BackupService, "generate_checksum_file", side_effect=ValueError
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message is not None
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()

    def test_zipping_step_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        mocker.patch.object(BackupService, "zip_folder", side_effect=ValueError)

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message is not None
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()
