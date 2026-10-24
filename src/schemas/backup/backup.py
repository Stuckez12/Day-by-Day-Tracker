from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.enums import BackupStatus, BackupTriggerMethod, BackupType
from src.schemas.backup.meta import RecordMetadata


class BackupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_backup_id: UUID | None = None
    celery_id: UUID | None = None
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


# TODO: Further filtering for specific params
class BackupFilters(BaseModel):
    is_child: bool | None = None
    is_processing: bool | None = None

    trigger_method: BackupTriggerMethod | None = None
    status: BackupStatus | None = None
    backup_type: BackupType | None = None

    min_duration: float | None = None
    max_duration: float | None = None
