from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class FileObjectMetadataSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    file_type: str = Field(..., alias="ContentType")
    byte_size: int = Field(..., alias="ContentLength")

    bucket: str
    directory: Path

    last_updated: datetime = Field(..., alias="LastModified")
