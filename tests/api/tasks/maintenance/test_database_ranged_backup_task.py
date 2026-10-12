from datetime import timedelta

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.common import utcnow
from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.models import BackupModel
from src.schemas import BackupSchema
from src.tasks import database_ranged_backup
from src.workflows import RangedBackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestDatabaseRangedBackupTask:
    def test_success_for_day(self, celery_worker: None, test_backup_session: Session):
        date_now = utcnow()
        task: AsyncResult = database_ranged_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value,
            start_date=date_now.strftime("%Y-%m-%d"),
            end_date=date_now.strftime("%Y-%m-%d"),
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.SUCCESS
        assert backup.backup_type == BackupType.RANGED_DAY
        assert backup.trigger_method == BackupTriggerMethod.MANUAL
        assert backup.duration is not None
        assert backup.duration > 0
        assert backup.error_message is None
        assert backup.error_traceback is None
        assert backup.meta is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.id == backup.id
        ).delete()
        test_backup_session.commit()

    def test_success_for_week(self, celery_worker: None, test_backup_session: Session):
        date_now = utcnow()
        start = date_now - timedelta(days=6)
        end = date_now

        task: AsyncResult = database_ranged_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value,
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.SUCCESS
        assert backup.backup_type == BackupType.RANGED_WEEK
        assert backup.trigger_method == BackupTriggerMethod.MANUAL
        assert backup.duration is not None
        assert backup.duration > 0
        assert backup.error_message is None
        assert backup.error_traceback is None
        assert backup.meta is not None

        test_backup_session.query(BackupModel).filter(
            BackupModel.id == backup.id
        ).delete()
        test_backup_session.commit()

    def test_date_range_failure(
        self, mocker: MockerFixture, celery_worker: None, test_backup_session: Session
    ):
        date_now = utcnow()
        inv_date_range = date_now - timedelta(days=2)
        mocker.patch.object(
            RangedBackupWorkflow,
            "create_ranged_backup",
            side_effect=RuntimeError,
        )

        task: AsyncResult = database_ranged_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value,
            start_date=inv_date_range.strftime("%Y-%m-%d"),
            end_date=date_now.strftime("%Y-%m-%d"),
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.FAILURE
        assert backup.trigger_method == BackupTriggerMethod.MANUAL
        assert backup.error_message == "Variable date range provided was not a week"
        assert backup.error_traceback is not None
        assert backup.meta is None

    def test_workflow_failure(
        self, mocker: MockerFixture, celery_worker: None, test_backup_session: Session
    ):
        date_now = utcnow()
        mocker.patch.object(
            RangedBackupWorkflow,
            "create_ranged_backup",
            side_effect=RuntimeError,
        )

        task: AsyncResult = database_ranged_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value,
            start_date=date_now.strftime("%Y-%m-%d"),
            end_date=date_now.strftime("%Y-%m-%d"),
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.FAILURE
        assert backup.trigger_method == BackupTriggerMethod.MANUAL
        assert backup.duration is not None
        assert backup.duration > 0
        assert backup.error_message is not None
        assert backup.error_traceback is not None
        assert backup.meta is None

        test_backup_session.query(BackupModel).filter(
            BackupModel.id == backup.id
        ).delete()
        test_backup_session.commit()
