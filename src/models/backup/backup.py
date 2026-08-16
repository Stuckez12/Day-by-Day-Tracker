from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as DBUUID, Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.models.backup.base import BackupBaseModel


if TYPE_CHECKING:
    from src.models.backup import MetaModel


class BackupModel(BackupBaseModel):
    __tablename__ = "backups"

    celery_id: Mapped[UUID] = mapped_column(DBUUID(as_uuid=True), nullable=False)
    trigger_method: Mapped[BackupTriggerMethod] = mapped_column(
        Enum(BackupTriggerMethod, native_enum=False), nullable=False
    )

    status: Mapped[BackupStatus] = mapped_column(
        Enum(BackupStatus, native_enum=False), nullable=False
    )
    backup_type: Mapped[BackupType] = mapped_column(
        Enum(BackupType, native_enum=False), nullable=False
    )
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    error_traceback: Mapped[str | None] = mapped_column(String, nullable=True)

    meta: Mapped["MetaModel | None"] = relationship(
        "MetaModel",
        cascade="all, delete-orphan",
        back_populates="backup",
    )
