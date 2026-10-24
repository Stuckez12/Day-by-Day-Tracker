import uuid
from datetime import datetime, timedelta

import pytest
from celery.exceptions import OperationalError
from pytest_mock import MockerFixture
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.enums import BackupType, TaskScheduleStatus
from src.models import BackupModel, BackupScheduleModel
from src.schemas import CreateScheduledBackupSchema, ScheduledBackupFilters
from src.schemas.backup.schedule import ScheduledBackupSchema
from src.services import BackupSchedulerService
from src.utils import utcnow


class TestCreateSchedule:
    def test_logical_success(
        self,
        test_backup_session: Session,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        task_id = uuid.uuid4()
        scheduled_for = datetime.now().date()

        data = CreateScheduledBackupSchema(
            celery_id=task_id,
            backup_type=BackupType.LOGICAL,
            scheduled_for=scheduled_for,
            date_range_start=None,
            date_range_end=None,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        assert result.celery_id == task_id
        assert result.backup_type == BackupType.LOGICAL
        assert result.scheduled_for == scheduled_for
        assert result.date_range_start is None
        assert result.date_range_end is None

        test_backup_session.delete(result)
        test_backup_session.commit()

    def test_ranged_week_success(
        self,
        test_backup_session: Session,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        task_id = uuid.uuid4()
        scheduled_for = datetime.now()
        start_time = scheduled_for - timedelta(days=6)
        end_time = scheduled_for

        scheduled_for = scheduled_for.date()

        data = CreateScheduledBackupSchema(
            celery_id=task_id,
            backup_type=BackupType.RANGED_WEEK,
            scheduled_for=scheduled_for,
            date_range_start=start_time,
            date_range_end=end_time,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        assert result.celery_id == task_id
        assert result.backup_type == BackupType.RANGED_WEEK
        assert result.scheduled_for == scheduled_for

        test_backup_session.delete(result)
        test_backup_session.commit()

    def test_ranged_day_success(
        self,
        test_backup_session: Session,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        task_id = uuid.uuid4()
        scheduled_for = datetime.now()

        data = CreateScheduledBackupSchema(
            celery_id=task_id,
            backup_type=BackupType.RANGED_DAY,
            scheduled_for=scheduled_for.date(),
            date_range_start=scheduled_for,
            date_range_end=scheduled_for,
        )

        result = test_backup_scheduler_service.create_schedule(data)
        assert result.celery_id == task_id
        assert result.backup_type == BackupType.RANGED_DAY
        assert result.scheduled_for == scheduled_for.date()
        assert result.date_range_start == scheduled_for
        assert result.date_range_end == scheduled_for

        test_backup_session.delete(result)
        test_backup_session.commit()


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
    @pytest.mark.parametrize(
        ("schedule_status", "regenerate_if_valid", "regenerate_if_invalid"),
        [
            (TaskScheduleStatus.QUEUED, False, True),
            (TaskScheduleStatus.PUBLISHED, False, False),
            (TaskScheduleStatus.RUNNING, False, False),
            (TaskScheduleStatus.SUCCESS, False, False),
            (TaskScheduleStatus.FAILED, True, True),
            (TaskScheduleStatus.CANCELLED, True, True),
        ],
    )
    @pytest.mark.parametrize("missing_task_id", [False, True])
    @pytest.mark.parametrize("dispatch_error", [None, "Connection error"])
    def test_regeneration_respects_schedule_status(
        self,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
        schedule_status: TaskScheduleStatus,
        regenerate_if_valid: bool,
        regenerate_if_invalid: bool,
        missing_task_id: bool,
        dispatch_error: str | None,
    ):
        schedule = test_logical_backup_schedule
        schedule.status = schedule_status

        if missing_task_id:
            schedule.celery_id = None

        schedule.dispatch_error = dispatch_error
        test_backup_session.commit()
        schedule_id = schedule.id

        should_regenerate = (
            regenerate_if_invalid
            if missing_task_id or dispatch_error is not None
            else regenerate_if_valid
        )

        try:
            result = test_backup_scheduler_service.generate_schedules(day_range=1)
            schedules = test_backup_session.query(BackupScheduleModel).all()
            assert len(schedules) == 1

            if should_regenerate:
                assert len(result) == 1
                assert schedules[0].id != schedule_id
                assert schedules[0].status == TaskScheduleStatus.QUEUED
                assert schedules[0].celery_id is not None
                assert schedules[0].dispatch_error is None

            else:
                assert result == []
                assert schedules[0].id == schedule_id
                assert schedules[0].status == schedule_status

        finally:
            test_backup_session.query(BackupScheduleModel).delete()
            test_backup_session.commit()

    def test_ignores_logical_backup_without_metadata(
        self,
        test_backup_session: Session,
        test_backup: BackupModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        assert test_backup.meta is None
        schedules = test_backup_scheduler_service.generate_schedules(day_range=1)

        try:
            assert len(schedules) == 1
            assert schedules[0].scheduled_for == utcnow().date()
            assert schedules[0].backup_type == BackupType.LOGICAL

        finally:
            test_backup_session.query(BackupScheduleModel).delete()
            test_backup_session.commit()

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
        test_ranged_day_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        test_backup_scheduler_service.create_schedule(
            CreateScheduledBackupSchema(
                celery_id=uuid.uuid4(),
                backup_type=BackupType.LOGICAL,
                scheduled_for=datetime.now().date() + timedelta(days=16),
            )
        )
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

    def test_second_invocation_creates_no_duplicates(
        self,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        schedules = test_backup_scheduler_service.generate_schedules(day_range=9)
        assert len(schedules) == 8

        try:
            original_ids = {
                row.id for row in test_backup_session.query(BackupScheduleModel).all()
            }

            result = test_backup_scheduler_service.generate_schedules(day_range=9)
            assert result == []
            assert {
                row.id for row in test_backup_session.query(BackupScheduleModel).all()
            } == original_ids

        finally:
            test_backup_session.query(BackupScheduleModel).delete()
            test_backup_session.commit()


class TestScheduleBackupTaskType:
    def test_successful_retry_clears_dispatch_error(
        self,
        mocker: MockerFixture,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):

        signature = mocker.patch("src.tasks.database_logical_backup.s")
        signature.return_value.apply_async.side_effect = OperationalError

        test_backup_scheduler_service.schedule_backup_task_type(
            test_logical_backup_schedule
        )
        test_backup_session.refresh(test_logical_backup_schedule)
        assert test_logical_backup_schedule.status == TaskScheduleStatus.QUEUED
        assert test_logical_backup_schedule.dispatch_error is not None

        signature.return_value.apply_async.side_effect = None

        test_backup_scheduler_service.schedule_backup_task_type(
            test_logical_backup_schedule
        )
        test_backup_session.refresh(test_logical_backup_schedule)
        assert signature.return_value.apply_async.call_count == 2
        assert test_logical_backup_schedule.status == TaskScheduleStatus.PUBLISHED
        assert test_logical_backup_schedule.dispatch_error is None


class TestAssignSchedule:
    def test_success(
        self,
        test_backup_session: Session,
        test_backup: BackupModel,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        test_logical_backup_schedule.status = TaskScheduleStatus.PUBLISHED
        test_backup_session.commit()

        test_backup_scheduler_service.assign_schedule(
            test_backup, test_logical_backup_schedule.scheduled_for
        )
        test_backup_session.refresh(test_logical_backup_schedule)
        assert test_logical_backup_schedule.backup_id == test_backup.id
        assert test_logical_backup_schedule.status == TaskScheduleStatus.RUNNING

    def test_missing_schedule(
        self,
        test_backup: BackupModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        with pytest.raises(NoResultFound):
            test_backup_scheduler_service.assign_schedule(
                test_backup, (utcnow() - timedelta(days=200)).date()
            )


class TestUpdateScheduleStatus:
    def test_success(
        self,
        test_backup_session: Session,
        test_backup: BackupModel,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        celery_id = test_logical_backup_schedule.celery_id
        test_logical_backup_schedule.backup_id = test_backup.id
        test_logical_backup_schedule.status = TaskScheduleStatus.RUNNING
        test_backup.set_successful()
        test_backup_session.commit()

        test_backup_scheduler_service.update_schedule_status(
            test_backup, TaskScheduleStatus.SUCCESS
        )
        test_backup_session.refresh(test_logical_backup_schedule)
        assert test_logical_backup_schedule.status == TaskScheduleStatus.SUCCESS
        assert test_backup.celery_id is None
        assert test_logical_backup_schedule.celery_id == celery_id
        assert test_logical_backup_schedule.backup_id == test_backup.id

        schedule = test_backup_scheduler_service.get_schedule(
            test_logical_backup_schedule.id
        )
        assert ScheduledBackupSchema.model_validate(schedule).celery_id == celery_id
        schedules = test_backup_scheduler_service.get_schedules_query(
            ScheduledBackupFilters()
        ).all()
        assert [
            ScheduledBackupSchema.model_validate(row).celery_id for row in schedules
        ] == [celery_id]

        assert test_backup_scheduler_service.generate_schedules(day_range=1) == []
        test_backup_session.refresh(test_logical_backup_schedule)
        assert test_logical_backup_schedule.status == TaskScheduleStatus.SUCCESS
        assert test_logical_backup_schedule.backup_id == test_backup.id

    def test_persists_failure(
        self,
        test_backup_session: Session,
        test_backup: BackupModel,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        celery_id = test_logical_backup_schedule.celery_id
        test_logical_backup_schedule.backup_id = test_backup.id
        test_logical_backup_schedule.status = TaskScheduleStatus.RUNNING
        test_backup.set_failed()
        test_backup_session.commit()

        test_backup_scheduler_service.update_schedule_status(
            test_backup, TaskScheduleStatus.FAILED
        )
        test_backup_session.refresh(test_logical_backup_schedule)
        assert test_logical_backup_schedule.status == TaskScheduleStatus.FAILED
        assert test_backup.celery_id is None
        assert test_logical_backup_schedule.celery_id == celery_id
        assert test_logical_backup_schedule.backup_id == test_backup.id

    def test_no_linked_schedule(
        self,
        test_backup_session: Session,
        test_backup: BackupModel,
        test_logical_backup_schedule: BackupScheduleModel,
        test_backup_scheduler_service: BackupSchedulerService,
    ):
        celery_id = test_logical_backup_schedule.celery_id

        test_backup_scheduler_service.update_schedule_status(
            test_backup, TaskScheduleStatus.SUCCESS
        )
        test_backup_session.refresh(test_logical_backup_schedule)
        assert test_logical_backup_schedule.backup_id is None
        assert test_logical_backup_schedule.status == TaskScheduleStatus.QUEUED
        assert test_logical_backup_schedule.celery_id == celery_id
