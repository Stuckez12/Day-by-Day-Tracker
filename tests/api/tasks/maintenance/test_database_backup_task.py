from pathlib import Path

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupStatus, BackupTriggerMethod
from src.models import BackupModel, RankerModel
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
        test_ranker: RankerModel,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.SUCCESS, backup.model_dump()
        assert backup.error_message is None
        assert backup.error_traceback is None

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
            BackupService,
            "create_logical_backup",
            side_effect=ValueError("create_logical_backup failed"),
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message == "ValueError: create_logical_backup failed"
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
            BackupService,
            "verify_backup_restoration",
            side_effect=ValueError("verify_backup_restoration failed"),
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message == "ValueError: verify_backup_restoration failed"
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
            BackupService,
            "generate_checksum_file",
            side_effect=ValueError("generate_checksum_file failed"),
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message == "ValueError: generate_checksum_file failed"
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
        test_ranker: RankerModel,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))
        mocker.patch.object(
            BackupService, "zip_folder", side_effect=ValueError("zip_folder failed")
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message == "ValueError: zip_folder failed"
        assert schema.error_traceback is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.celery_id == schema.celery_id
        ).delete()
        test_backup_session.commit()
