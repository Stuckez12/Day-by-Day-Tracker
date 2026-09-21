from datetime import datetime
from pathlib import Path

from botocore.response import StreamingBody
from pydantic import BaseModel, ConfigDict, Field


class FileObjectMetadataSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    file_type: str = Field(..., alias="ContentType")
    byte_size: int = Field(..., alias="ContentLength")

    bucket: str
    directory: Path

    last_updated: datetime = Field(..., alias="LastModified")


class FileObjectDownloadSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: StreamingBody = Field(..., alias="Body")

    file_type: str = Field(..., alias="ContentType")
    byte_size: int = Field(..., alias="ContentLength")
