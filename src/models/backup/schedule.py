from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.utils import utcnow
from src.enums import BackupType, TaskScheduleStatus
from src.models.backup.base import BackupBaseModel


if TYPE_CHECKING:
    from src.models.backup import BackupModel


class BackupScheduleModel(BackupBaseModel):
    __tablename__ = "backup-scheduler"

    celery_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    backup_id: Mapped[UUID] = mapped_column(
        ForeignKey("backups.id", ondelete="CASCADE"), nullable=True, default=None
    )

    backup_type: Mapped[BackupType] = mapped_column(Enum(BackupType), nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[TaskScheduleStatus] = mapped_column(
        Enum(TaskScheduleStatus), nullable=False
    )

    date_range_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=False)
    date_range_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=False)

    dispatched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    dispatch_error: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )

    backup: Mapped[BackupModel] = relationship(
        "BackupModel",
        back_populates="schedule",
    )

    def __init__(
        self,
        celery_id: uuid.UUID,
        backup_type: BackupType,
        scheduled_for: datetime,
        date_range_start: datetime | None = None,
        date_range_end: datetime | None = None,
    ):
        self.celery_id = celery_id
        self.backup_type = backup_type
        self.scheduled_for = scheduled_for
        self.date_range_start = date_range_start
        self.date_range_end = date_range_end

        self.status = TaskScheduleStatus.QUEUED
        self.dispatched_at = utcnow()
