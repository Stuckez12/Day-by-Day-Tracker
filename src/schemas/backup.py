from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.settings import app_config


class BackupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    celery_id: UUID
    trigger_method: BackupTriggerMethod
    status: BackupStatus
    backup_type: BackupType
    duration: float | None = None
    error_message: str | None = None
    error_traceback: str | None = None


class BackupCreate(BaseModel):
    celery_id: str
    trigger_method: BackupTriggerMethod
    status: BackupStatus
    backup_type: BackupType


MetadataFileType = Literal["backup", "checksum"]


class MetadataChecksum(BaseModel):
    algorithm: str
    file_name: str
    verified: bool = False
    last_verified: datetime | None = None


class MetadataTool(BaseModel):
    name: str
    version: str


class MetadataFiles(BaseModel):
    name: str
    type: MetadataFileType
    size_bytes: int


class MetadataDateRange(BaseModel):
    start: datetime
    end: datetime


class MetadataData(BaseModel):
    date_range: MetadataDateRange


class Metadata(BaseModel):
    schema_version: int = 1

    backup_id: str
    backup_type: BackupType
    created_at: datetime

    database_alembic_version: str
    app_version: str = app_config.APP_VERSION

    checksum: MetadataChecksum
    tool: MetadataTool
    files: list[MetadataFiles]
    data: MetadataData

    def get_file_type_data(self, file_type: MetadataFileType) -> MetadataFiles | None:
        for file in self.files:
            if file.type == file_type:
                return file

        return None
