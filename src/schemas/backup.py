import uuid

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BackupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    backup_date: datetime
    file_path: str
