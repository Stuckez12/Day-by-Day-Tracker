from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.enums import BackupType, TaskScheduleStatus
from src.schemas.backup.backup import BackupSchema


class ScheduledBackupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    celery_id: UUID
    backup_id: UUID | None = None

    backup_type: BackupType
    scheduled_for: datetime
    status: TaskScheduleStatus

    date_range_start: datetime | None = None
    date_range_end: datetime | None = None

    dispatched_at: datetime
    dispatch_error: str | None = None

    backup: BackupSchema | None = None


class CreateScheduledBackupSchema(BaseModel):
    celery_id: UUID

    backup_type: BackupType
    scheduled_for: datetime

    date_range_start: datetime | None = None
    date_range_end: datetime | None = None


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
