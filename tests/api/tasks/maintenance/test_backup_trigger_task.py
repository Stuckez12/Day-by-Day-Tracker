import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import TaskScheduleStatus
from src.models import BackupScheduleModel
from src.services import BackupSchedulerService
from src.tasks import backup_trigger, database_logical_backup


@pytest.mark.usefixtures("mock_task_db")
class TestBackupTriggerTask:
    def test_dispatches_today_schedule(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        signature = mocker.patch.object(database_logical_backup, "s")

        backup_trigger.apply_async()
        test_backup_session.refresh(test_logical_backup_schedule)

        signature.assert_called_once()
        signature.return_value.apply_async.assert_called_once_with(
            task_id=str(test_logical_backup_schedule.celery_id), countdown=300
        )
        assert test_logical_backup_schedule.status == TaskScheduleStatus.PUBLISHED
        assert test_logical_backup_schedule.dispatch_error is None

    def test_no_schedule(self, mocker: MockerFixture, celery_worker: None):
        dispatch = mocker.patch.object(
            BackupSchedulerService, "schedule_backup_task_type"
        )

        backup_trigger.apply_async()

        dispatch.assert_not_called()

    def test_repeated_invocation_does_not_duplicate_dispatch(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        signature = mocker.patch.object(database_logical_backup, "s")

        backup_trigger.apply_async()
        backup_trigger.apply_async()
        test_backup_session.refresh(test_logical_backup_schedule)

        signature.return_value.apply_async.assert_called_once_with(
            task_id=str(test_logical_backup_schedule.celery_id), countdown=300
        )
        assert test_logical_backup_schedule.status == TaskScheduleStatus.PUBLISHED

    def test_ignores_running_schedule(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        test_logical_backup_schedule.status = TaskScheduleStatus.RUNNING
        test_backup_session.commit()
        signature = mocker.patch.object(database_logical_backup, "s")

        backup_trigger.apply_async()
        test_backup_session.refresh(test_logical_backup_schedule)

        signature.assert_not_called()
        assert test_logical_backup_schedule.status == TaskScheduleStatus.RUNNING
