from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as DBUUID, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.models.backup.base import BackupBaseModel


if TYPE_CHECKING:
    from src.models.backup import BackupScheduleModel, MetaModel


class BackupModel(BackupBaseModel):
    __tablename__ = "backups"

    parent_backup_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("backups.id", ondelete="SET NULL"), default=None, nullable=True
    )
    celery_id: Mapped[UUID | None] = mapped_column(DBUUID(as_uuid=True), nullable=True)
    trigger_method: Mapped[BackupTriggerMethod] = mapped_column(
        Enum(BackupTriggerMethod), nullable=False
    )

    status: Mapped[BackupStatus] = mapped_column(Enum(BackupStatus), nullable=False)
    backup_type: Mapped[BackupType] = mapped_column(Enum(BackupType), nullable=False)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    error_traceback: Mapped[str | None] = mapped_column(String, nullable=True)

    parent_backup: Mapped[BackupModel | None] = relationship(
        "BackupModel", back_populates="children_backup", remote_side="BackupModel.id"
    )
    children_backup: Mapped[list[BackupModel]] = relationship(
        "BackupModel", back_populates="parent_backup"
    )

    meta: Mapped[MetaModel | None] = relationship(
        "MetaModel", back_populates="backup", cascade="all, delete-orphan"
    )
    schedule: Mapped[BackupScheduleModel | None] = relationship(
        "BackupScheduleModel", back_populates="backup", cascade="all"
    )

    @property
    def is_being_processed(self) -> bool:
        return (
            self.status in [BackupStatus.RUNNING, BackupStatus.VERIFYING]
            or self.celery_id is not None
        )

    def set_running(self, celery_id: UUID | str):
        if isinstance(celery_id, str):
            celery_id = UUID(celery_id)

        self.status = BackupStatus.RUNNING
        self.celery_id = celery_id

    def set_verifying(self, celery_id: UUID | str):
        if isinstance(celery_id, str):
            celery_id = UUID(celery_id)

        self.status = BackupStatus.VERIFYING
        self.celery_id = celery_id

    def set_successful(self):
        self.status = BackupStatus.SUCCESS
        self.celery_id = None

    def set_failed(self):
        self.status = BackupStatus.FAILURE
        self.celery_id = None
