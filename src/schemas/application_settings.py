from uuid import UUID

from pydantic import BaseModel


class ApplicationSettingsSchema(BaseModel):
    RESTORE_DATABASE_TO_BACKUP_ID: UUID | None = None
