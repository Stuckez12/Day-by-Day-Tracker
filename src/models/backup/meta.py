from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.backup.base import BackupBaseModel
from src.settings import app_config


if TYPE_CHECKING:
    from src.models.backup import BackupModel


class MetaModel(BackupBaseModel):
    __tablename__ = "meta"

    backup_id: Mapped[str] = mapped_column(
        ForeignKey("backups.id", ondelete="CASCADE"), nullable=False
    )

    # Database Data
    database_alembic_version: Mapped[str] = mapped_column(String, nullable=False)
    app_version: Mapped[str] = mapped_column(
        String, default=app_config.APP_VERSION, nullable=False
    )

    # Checksum Data
    algorithm: Mapped[str] = mapped_column(String, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    last_verified: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Tool Used
    tool_used: Mapped[str] = mapped_column(String, nullable=False)
    tool_version: Mapped[str] = mapped_column(String, nullable=False)

    # Database Data
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    date_range_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_range_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # File Data
    zip_filename: Mapped[str] = mapped_column(String, nullable=False)
    zip_path: Mapped[str] = mapped_column(String, nullable=False)
    zip_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    backup: Mapped["BackupModel"] = relationship(
        "BackupModel",
        back_populates="meta",
    )
