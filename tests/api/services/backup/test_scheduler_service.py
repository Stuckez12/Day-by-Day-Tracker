import uuid
from datetime import datetime, timedelta

import pytest
from celery.exceptions import OperationalError
from pytest_mock import MockerFixture
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.enums import BackupTriggerMethod, BackupType
from src.models import BackupScheduleModel
from src.schemas import CreateScheduledBackupSchema
from src.schemas.backup.schedule import ScheduledBackupSchema
from src.services import BackupSchedulerService
from src.utils import utcnow


class TestCreateSchedule:
    def test_logical_success(
        self,
        mocker: MockerFixture,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        task_id = uuid.uuid4()
        task = mocker.patch(
            "src.tasks.database_logical_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )
        do_not_call_task = mocker.patch(
            "src.tasks.database_ranged_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )

        scheduled_for = datetime.now()

        data = CreateScheduledBackupSchema(
            celery_id=task_id,
            backup_type=BackupType.LOGICAL,
            scheduled_for=scheduled_for,
            date_range_start=None,
            date_range_end=None,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        test_backup_scheduler_service.schedule_backup_task_type(result)
        assert result.celery_id == task_id
        assert result.backup_type == BackupType.LOGICAL
        assert result.scheduled_for == scheduled_for.date()
        assert result.date_range_start is None
        assert result.date_range_end is None

        task.s.assert_called_once_with(
            date_triggered=utcnow().strftime("%Y-%m-%d"),
            trigger=BackupTriggerMethod.SCHEDULED.value,
        )
        task.s.return_value.apply_async.assert_called_once_with(
            task_id=str(task_id), countdown=300
        )
        do_not_call_task.s.assert_not_called()

    def test_ranged_week_success(
        self,
        mocker: MockerFixture,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        task_id = uuid.uuid4()
        do_not_call_task = mocker.patch(
            "src.tasks.database_logical_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )
        task = mocker.patch(
            "src.tasks.database_ranged_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )

        scheduled_for = datetime.now()
        start_time = scheduled_for - timedelta(days=6)

        data = CreateScheduledBackupSchema(
            celery_id=task_id,
            backup_type=BackupType.RANGED_WEEK,
            scheduled_for=scheduled_for,
            date_range_start=start_time,
            date_range_end=scheduled_for,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        test_backup_scheduler_service.schedule_backup_task_type(result)
        assert result.celery_id == task_id
        assert result.backup_type == BackupType.RANGED_WEEK
        assert result.scheduled_for == scheduled_for.date()

        task.s.assert_called_once_with(
            date_triggered=utcnow().strftime("%Y-%m-%d"),
            trigger=BackupTriggerMethod.SCHEDULED.value,
            start_date=start_time.strftime("%Y-%m-%d"),
            end_date=scheduled_for.strftime("%Y-%m-%d"),
        )
        task.s.return_value.apply_async.assert_called_once_with(
            task_id=str(task_id), countdown=300
        )
        do_not_call_task.s.assert_not_called()

    def test_ranged_day_success(
        self,
        mocker: MockerFixture,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        task_id = uuid.uuid4()
        do_not_call_task = mocker.patch(
            "src.tasks.database_logical_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )
        task = mocker.patch(
            "src.tasks.database_ranged_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )

        scheduled_for = datetime.now()

        data = CreateScheduledBackupSchema(
            celery_id=task_id,
            backup_type=BackupType.RANGED_DAY,
            scheduled_for=scheduled_for,
            date_range_start=scheduled_for,
            date_range_end=scheduled_for,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        test_backup_scheduler_service.schedule_backup_task_type(result)
        assert result.celery_id == task_id
        assert result.backup_type == BackupType.RANGED_DAY
        assert result.scheduled_for == scheduled_for.date()
        assert result.date_range_start == scheduled_for
        assert result.date_range_end == scheduled_for

        task.s.assert_called_once_with(
            date_triggered=utcnow().strftime("%Y-%m-%d"),
            trigger=BackupTriggerMethod.SCHEDULED.value,
            start_date=scheduled_for.strftime("%Y-%m-%d"),
            end_date=scheduled_for.strftime("%Y-%m-%d"),
        )
        task.s.return_value.apply_async.assert_called_once_with(
            task_id=str(task_id), countdown=300
        )
        do_not_call_task.s.assert_not_called()

    def test_dispatch_error(
        self,
        mocker: MockerFixture,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        mocker.patch.object(
            BackupSchedulerService,
            "_schedule_backup_task_type",
            side_effect=OperationalError,
        )

        scheduled_for = datetime.now()
        data = CreateScheduledBackupSchema(
            celery_id=uuid.uuid4(),
            backup_type=BackupType.LOGICAL,
            scheduled_for=scheduled_for,
            date_range_start=None,
            date_range_end=None,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        test_backup_scheduler_service.schedule_backup_task_type(result)
        assert result.celery_id == data.celery_id
        assert result.backup_type == BackupType.LOGICAL
        assert result.scheduled_for == scheduled_for.date()
        assert result.date_range_start is None
        assert result.date_range_end is None
        assert (
            result.dispatch_error
            == f"Unable to schedule backup task for {scheduled_for.strftime('%Y-%m-%d')}. Connection error"
        )

    # Usefulness: 9/10
    def test_persists_schedule_without_dispatching(self):
        pass


# @pytest.mark.xfail(strict=True, reason="get_schedule is not implemented")
class TestGetSchedule:
    def test_success(
        self,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        result = test_backup_scheduler_service.get_schedule(
            test_logical_backup_schedule.id
        )
        assert result == test_logical_backup_schedule

    def test_not_found(
        self,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        with pytest.raises(NoResultFound):
            test_backup_scheduler_service.get_schedule(uuid.uuid4())


class TestDeleteSchedule:
    def test_success(
        self,
        test_backup_session: Session,
        test_backup_scheduler_service: BackupSchedulerService,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        schedule_id = test_logical_backup_schedule.id

        test_backup_scheduler_service.delete_schedule(test_logical_backup_schedule)

        result = (
            test_backup_session.query(BackupScheduleModel)
            .filter(BackupScheduleModel.id == schedule_id)
            .first()
        )
        assert result is None


class TestGenerateSchedules:
    def test_success(
        self,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        result = test_backup_scheduler_service.generate_schedules(day_range=9)
        assert len(result) == 8

        schedules = [
            ScheduledBackupSchema.model_validate(schedule) for schedule in result
        ]
        assert test_logical_backup_schedule.id not in [
            schedule.id for schedule in schedules
        ]

        test_backup_session.query(BackupScheduleModel).delete()
        test_backup_session.commit()

    def test_backup_type_ordering(
        self,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        result = test_backup_scheduler_service.generate_schedules(day_range=29)
        assert len(result) == 28

        schedules = [
            ScheduledBackupSchema.model_validate(schedule) for schedule in result
        ]
        assert [schedule.backup_type for schedule in schedules] == [
            *[BackupType.RANGED_DAY] * 6,
            BackupType.RANGED_WEEK,
            *[BackupType.RANGED_DAY] * 6,
            BackupType.RANGED_WEEK,
            *[BackupType.RANGED_DAY] * 6,
            BackupType.RANGED_WEEK,
            *[BackupType.RANGED_DAY] * 6,
            BackupType.LOGICAL,
        ]

        test_backup_session.query(BackupScheduleModel).delete()
        test_backup_session.commit()

    def test_selective_backup_type_ordering(
        self,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
        test_ranged_day_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        test_logical_backup_schedule.scheduled_for = (
            datetime.now() + timedelta(days=16)
        ).date()
        test_backup_session.commit()
        result = test_backup_scheduler_service.generate_schedules(day_range=29)
        assert len(result) == 27

        schedules = [
            ScheduledBackupSchema.model_validate(schedule) for schedule in result
        ]
        assert [schedule.backup_type for schedule in schedules] == [
            *[BackupType.RANGED_DAY] * 6,
            BackupType.RANGED_WEEK,
            *[BackupType.RANGED_DAY] * 6,
            BackupType.RANGED_WEEK,
            *[BackupType.RANGED_DAY] * 5,
            BackupType.RANGED_WEEK,
            *[BackupType.RANGED_DAY] * 6,
            BackupType.LOGICAL,
        ]
        assert test_ranged_day_backup_schedule.scheduled_for not in [
            schedule.scheduled_for for schedule in schedules
        ]

        test_backup_session.query(BackupScheduleModel).delete()
        test_backup_session.commit()

    def test_second_invocation_creates_no_duplicates(self):
        pass


class TestScheduleBackupTaskType:
    def test_successful_retry_clears_dispatch_error(self):
        pass


class TestAssignSchedule:
    def test_success(self):
        pass

    def test_missing_schedule(self):
        pass


class TestUpdateScheduleStatus:
    def test_success(self):
        pass

    def test_persists_failure(self):
        pass

    def test_no_linked_schedule(self):
        pass
