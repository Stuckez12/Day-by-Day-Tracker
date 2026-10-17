from datetime import date, datetime, timedelta
from typing import cast
from uuid import UUID

from sqlalchemy.orm import Query, Session

from src.enums import BackupType
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

    def create_schedule(self, data: CreateScheduledBackupSchema):
        pass

    def get_schedule(self, schedule_id: UUID):
        pass

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
                >= data.scheduled_to + timedelta(days=1)
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

    def generate_schedules(self):
        day_range = 130

        today = utcnow()
        from_date = today
        to_date = today + timedelta(days=day_range)

        query = self.get_schedules_query(
            ScheduledBackupFilters(
                scheduled_from=from_date,
                scheduled_to=to_date,
            )
        )

        future_schedules: list[BackupScheduleModel] = query.all()
        mapped_schedules = {
            schedule.scheduled_for.date(): schedule for schedule in future_schedules
        }

        dates_to_schedule = self._get_unscheduled_dates(
            mapped_schedules, today, day_range
        )

        last_logical_backup_query = self.get_backups_query(
            BackupFilters(backup_type=BackupType.LOGICAL)
        )
        last_logical_backup = last_logical_backup_query.first()

        backup_date_order = self._calculate_backup_type_order_from_logical_to_date(
            last_logical_backup, to_date
        )

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
    ) -> dict[date, BackupType]:
        backup_type_order: dict[date, BackupType] = {}

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
                4  # TODO: Replace with application settings param
            )

            is_ranged_week_backup = date_offset % 7 == 0
            is_logical_backup = date_offset % (7 * weeks_between_logical_backups) == 0

            # Decide on the order
            backup_type_order[current_date] = BackupType.RANGED_DAY

            if is_logical_backup:
                backup_type_order[current_date] = BackupType.LOGICAL

            elif is_ranged_week_backup:
                backup_type_order[current_date] = BackupType.RANGED_WEEK

        return backup_type_order
