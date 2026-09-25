from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.settings import app_config


MetadataFileType = Literal["backup"]


# TODO: move metadata schemas into new file and group with backup file in backup folder
class MetadataChecksum(BaseModel):
    algorithm: str
    value: str
    verified: bool = False
    last_verified: datetime | None = None


class MetadataTool(BaseModel):
    name: str
    version: str


class MetadataFiles(BaseModel):
    name: str
    type: MetadataFileType
    size_bytes: int
    checksum: MetadataChecksum


class MetadataDateRange(BaseModel):
    start: datetime
    end: datetime


class MetadataData(BaseModel):
    date_range: MetadataDateRange


class Metadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schema_version: int = 1

    backup_id: str
    backup_type: BackupType
    created_at: datetime

    database_alembic_version: str
    app_version: str = app_config.APP_VERSION

    tool: MetadataTool
    files: list[MetadataFiles]
    data: MetadataData

    def get_checksum_data(self) -> MetadataChecksum:
        """All checksums should be done by the same algorithm"""
        if len(self.files) == 0:
            raise ValueError("No files in the metadata object have been recorded")

        return self.files[0].checksum


class RecordMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    backup_id: UUID

    # Database Data
    database_alembic_version: str
    app_version: str

    # Checksum Data
    algorithm: str
    verified: bool
    last_verified: datetime | None = None

    # Tool Used
    tool_used: str
    tool_version: str

    # Database Data
    date_range_start: datetime
    date_range_end: datetime

    # File Data
    zip_filename: str
    zip_path: str
    zip_size_bytes: int


class BackupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    celery_id: UUID
    trigger_method: BackupTriggerMethod
    status: BackupStatus
    backup_type: BackupType
    duration: float | None = None
    error_message: str | None = None
    error_traceback: str | None = None

    meta: RecordMetadata | None = None


class VerifiedBackupResultSchema(BaseModel):
    id: UUID
    celery_id: UUID
    verified: bool
    backup_type: BackupType | None = None
    error_message: str | None = None
    error_traceback: str | None = None


class BackupCreate(BaseModel):
    celery_id: str
    trigger_method: BackupTriggerMethod
    status: BackupStatus
    backup_type: BackupType
