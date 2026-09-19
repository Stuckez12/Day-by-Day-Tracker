from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.backup.base import BackupBaseModel
from src.settings import app_config


if TYPE_CHECKING:
    from src.models.backup import BackupModel
    from src.schemas import Metadata


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
    last_verified: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Tool Used
    tool_used: Mapped[str] = mapped_column(String, nullable=False)
    tool_version: Mapped[str] = mapped_column(String, nullable=False)

    # Database Data
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

    def __init__(self, metadata_schema: Metadata, zipped_file: Path):
        checksum_data = metadata_schema.get_checksum_data()

        # Identification
        self.backup_id = metadata_schema.backup_id
        self.database_alembic_version = metadata_schema.database_alembic_version

        # Checksum
        self.algorithm = checksum_data.algorithm
        self.verified = checksum_data.verified
        self.last_verified = checksum_data.last_verified

        # Tool
        self.tool_used = metadata_schema.tool.name
        self.tool_version = metadata_schema.tool.version

        # Data
        self.date_range_start = metadata_schema.data.date_range.start
        self.date_range_end = metadata_schema.data.date_range.end

        # Zipped backup file
        self.zip_filename = zipped_file.name
        self.zip_path = str(zipped_file)
        self.zip_size_bytes = zipped_file.stat().st_size
