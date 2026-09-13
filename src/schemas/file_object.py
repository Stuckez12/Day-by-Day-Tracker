from pydantic import BaseModel

from src.enums.object_type import ObjectType


class FileObjectUploaded(BaseModel):
    message: str
    bucket: ObjectType
    filename: str
