import uuid
from datetime import date, datetime, time, timedelta
from typing import cast
from uuid import UUID

from celery.exceptions import OperationalError
from sqlalchemy.orm import Query, Session

from src.enums import BackupType
from src.enums.backup.status import BackupStatus
from src.enums.backup.trigger_method import BackupTriggerMethod
from src.main import celery_app
from src.models import BackupModel, BackupScheduleModel, MetaModel
from src.schemas import (
    BackupFilters,
    CreateScheduledBackupSchema,
    ScheduledBackupFilters,
)
from src.utils import utcnow

from .backup import BackupService


class BackupSchedulerService(BackupService):
    def __init__(self, db: Session, backup_db: Session) -> None:
        super().__init__(db=db, backup_db=backup_db)
        self.model = BackupScheduleModel

    def create_schedule(self, data: CreateScheduledBackupSchema) -> BackupScheduleModel:
        model = BackupScheduleModel(data)

        self.backup_db.add(model)

        try:
            self._schedule_backup_task_type(model)

        except OperationalError:
            model.dispatch_error = f"Unable to schedule backup task for {model.scheduled_for.strftime('%Y-%m-%d')}. Connection error"

        self.backup_db.commit()
        self.backup_db.refresh(model)

        return model

    def _schedule_backup_task_type(self, model: BackupScheduleModel) -> None:
        from src.tasks import database_logical_backup, database_ranged_backup

        match model.backup_type:
            case BackupType.LOGICAL:
                database_logical_backup.s(
                    trigger=BackupTriggerMethod.SCHEDULED.value
                ).apply_async(task_id=str(model.celery_id), eta=model.scheduled_for)

            case BackupType.RANGED_WEEK | BackupType.RANGED_DAY:
                database_ranged_backup.s(
                    trigger=BackupTriggerMethod.SCHEDULED.value,
                    start_date=cast(datetime, model.date_range_start).strftime(
                        "%Y-%m-%d"
                    ),
                    end_date=cast(datetime, model.date_range_end).strftime("%Y-%m-%d"),
                ).apply_async(task_id=str(model.celery_id), eta=model.scheduled_for)

    def get_schedule(self, schedule_id: UUID) -> BackupScheduleModel:
        return (
            self.backup_db.query(BackupScheduleModel)
            .filter(BackupScheduleModel.id == schedule_id)
            .one()
        )

    def delete_schedule(self, schedule: BackupScheduleModel) -> None:
        celery_app.control.revoke(str(schedule.celery_id), terminate=False)

        self.backup_db.delete(schedule)
        self.backup_db.commit()

    def get_schedules_query(
        self, data: ScheduledBackupFilters
    ) -> Query[BackupScheduleModel]:
        query = self.backup_db.query(BackupScheduleModel)

        if data.backup_type is not None:
            query = query.filter(BackupScheduleModel.backup_type == data.backup_type)

        if data.scheduled_from is not None:
            query = query.filter(
                BackupScheduleModel.scheduled_for >= data.scheduled_from
            )

        if data.scheduled_to is not None:
            query = query.filter(
                BackupScheduleModel.scheduled_for
                <= data.scheduled_to + timedelta(days=1)
            )

        if data.status is not None:
            query = query.filter(BackupScheduleModel.status == data.status)

        if data.date_from is not None:
            query = query.filter(BackupScheduleModel.date_range_start >= data.date_from)

        if data.date_to is not None:
            query = query.filter(BackupScheduleModel.date_range_end <= data.date_to)

        if data.dispatched_from is not None:
            query = query.filter(
                BackupScheduleModel.dispatched_at >= data.dispatched_from
            )

        if data.dispatched_to is not None:
            query = query.filter(
                BackupScheduleModel.dispatched_at <= data.dispatched_to
            )

        query = query.order_by(BackupScheduleModel.scheduled_for.desc())

        return query

    def generate_schedules(self, day_range: int = 130) -> list[BackupScheduleModel]:
        # day_range = 130  # TODO: Replace with configurable application settings param

        today = utcnow()
        from_date = today.date()
        to_date = (today + timedelta(days=day_range)).date()

        query = self.get_schedules_query(
            ScheduledBackupFilters(scheduled_from=from_date, scheduled_to=to_date)
        )

        future_schedules: list[BackupScheduleModel] = query.all()
        mapped_schedules = {
            schedule.scheduled_for.date(): schedule for schedule in future_schedules
        }

        dates_to_schedule = self._get_unscheduled_dates(
            mapped_schedules, today, day_range
        )

        if len(dates_to_schedule) == 0:
            return []

        last_logical_backup_query = self.get_backups_query(
            BackupFilters(backup_type=BackupType.LOGICAL, status=BackupStatus.SUCCESS)
        )
        last_logical_backup = last_logical_backup_query.first()

        backup_date_order = self._calculate_backup_type_order_from_logical_to_date(
            last_logical_backup, to_date
        )

        created_schedules: list[BackupScheduleModel] = []

        for schedule_this_date in dates_to_schedule:
            backup_date_type = backup_date_order.get(schedule_this_date, None)

            if backup_date_type is None:
                continue

            backup_type = cast(BackupType, backup_date_type.get("type"))
            scheduled_for = datetime.combine(schedule_this_date, time(23, 59))

            date_range_start = cast(datetime | None, backup_date_type.get("date_start"))
            date_range_end = cast(datetime | None, backup_date_type.get("date_end"))

            data = CreateScheduledBackupSchema(
                celery_id=uuid.uuid4(),
                backup_type=backup_type,
                scheduled_for=scheduled_for,
                date_range_start=date_range_start,
                date_range_end=date_range_end,
            )

            new_schedule = self.create_schedule(data)

            created_schedules.append(new_schedule)

        return created_schedules

    def _get_unscheduled_dates(
        self,
        mapped_schedules: dict[date, BackupScheduleModel],
        today: datetime,
        day_range: int,
    ) -> list[date]:
        schedule_dates_to_populate: list[date] = []

        for day_count in range(0, day_range):
            date_select = (today + timedelta(days=day_count)).date()

            recorded_schedule = mapped_schedules.get(date_select, None)

            if recorded_schedule is None:
                schedule_dates_to_populate.append(date_select)

            elif (
                recorded_schedule.celery_id is None
                or recorded_schedule.dispatch_error is not None
            ):
                self.backup_db.delete(recorded_schedule)
                self.backup_db.flush()

                schedule_dates_to_populate.append(date_select)

        return schedule_dates_to_populate

    def _calculate_backup_type_order_from_logical_to_date(
        self, logical_backup: BackupModel | None, to_date: date
    ) -> dict[date, dict[str, BackupType | date | None]]:
        backup_type_order: dict[date, dict[str, BackupType | date | None]] = {}

        logical_backup_date: date = utcnow().date()

        if logical_backup:
            logical_backup_date = cast(
                MetaModel, logical_backup.meta
            ).date_range_end.date()

        if logical_backup_date > to_date:
            raise IndexError(
                "Unable to calculate the order of backups when the last targeted date is before the last logical backup"
            )

        days_until_last_targeted_date = (to_date - logical_backup_date).days + 1

        for date_offset in range(0, days_until_last_targeted_date):
            current_date = logical_backup_date + timedelta(days=date_offset)

            weeks_between_logical_backups = (
                4  # TODO: Replace with configurable application settings param
            )

            is_ranged_week_backup = date_offset % 7 == 0
            is_logical_backup = date_offset % (7 * weeks_between_logical_backups) == 0

            # Decide on the order
            backup_type_data: dict[str, BackupType | date | None] = {
                "type": BackupType.RANGED_DAY,
                "date_start": current_date,
                "date_end": current_date,
            }
            backup_type_order[current_date] = backup_type_data

            if is_logical_backup:
                backup_type_data["type"] = BackupType.LOGICAL
                backup_type_data["date_start"] = None
                backup_type_data["date_end"] = None

                backup_type_order[current_date] = backup_type_data

            elif is_ranged_week_backup:
                backup_type_data["type"] = BackupType.RANGED_WEEK
                backup_type_data["date_start"] = current_date - timedelta(days=6)
                backup_type_data["date_end"] = current_date

                backup_type_order[current_date] = backup_type_data

        return backup_type_order
