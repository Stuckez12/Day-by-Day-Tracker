from __future__ import annotations

from datetime import date, datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from src.enums import BackupType, TaskScheduleStatus
from src.schemas.backup.backup import BackupSchema


class ScheduledBackupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    celery_id: UUID
    backup_id: UUID | None = None

    backup_type: BackupType
    scheduled_for: date
    status: TaskScheduleStatus

    date_range_start: datetime | None = None
    date_range_end: datetime | None = None

    dispatched_at: datetime
    dispatch_error: str | None = None

    backup: BackupSchema | None = None


class CreateScheduledBackupSchema(BaseModel):
    celery_id: UUID

    backup_type: BackupType
    scheduled_for: date

    date_range_start: datetime | None = None
    date_range_end: datetime | None = None

    @model_validator(mode="after")
    def validate_backup_range(self) -> Self:
        if self.backup_type not in (
            BackupType.LOGICAL,
            BackupType.RANGED_DAY,
            BackupType.RANGED_WEEK,
        ):
            raise ValueError("Backup type cannot be scheduled")

        if self.backup_type == BackupType.LOGICAL:
            return self

        if self.date_range_start is None or self.date_range_end is None:
            raise ValueError("Ranged backups require both start and end dates")

        start_date = self.date_range_start.date()
        end_date = self.date_range_end.date()

        if start_date > end_date:
            raise ValueError("Start date must be on or before end date")

        days = (end_date - start_date).days

        if self.backup_type == BackupType.RANGED_DAY and days != 0:
            raise ValueError("Daily backups must cover a single calendar day")

        if self.backup_type == BackupType.RANGED_WEEK and days != 6:
            raise ValueError("Weekly backups must cover seven calendar days")

        return self


# TODO: Further filtering for specific params maybe
class ScheduledBackupFilters(BaseModel):
    backup_type: BackupType | None = None
    status: TaskScheduleStatus | None = None

    scheduled_from: date | None = None
    scheduled_to: date | None = None

    date_from: datetime | None = None
    date_to: datetime | None = None

    dispatched_from: datetime | None = None
    dispatched_to: datetime | None = None
