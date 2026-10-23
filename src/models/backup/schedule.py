from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import BackupType, TaskScheduleStatus
from src.models.backup.base import BackupBaseModel
from src.schemas.backup.schedule import CreateScheduledBackupSchema
from src.utils import utcnow


if TYPE_CHECKING:
    from src.models.backup import BackupModel


class BackupScheduleModel(BackupBaseModel):
    __tablename__ = "backup-scheduler"

    celery_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, nullable=True, default=None
    )
    backup_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("backups.id", ondelete="CASCADE"), nullable=True, default=None
    )

    backup_type: Mapped[BackupType] = mapped_column(Enum(BackupType), nullable=False)
    scheduled_for: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    status: Mapped[TaskScheduleStatus] = mapped_column(
        Enum(TaskScheduleStatus), nullable=False
    )

    date_range_start: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    date_range_end: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    dispatched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    dispatch_error: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )

    backup: Mapped[BackupModel] = relationship("BackupModel", back_populates="schedule")

    def __init__(self, data: CreateScheduledBackupSchema):
        self.celery_id = data.celery_id
        self.backup_type = data.backup_type
        self.scheduled_for = data.scheduled_for
        self.date_range_start = data.date_range_start
        self.date_range_end = data.date_range_end

        self.status = TaskScheduleStatus.QUEUED
        self.dispatched_at = utcnow()
