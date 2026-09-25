from pydantic import BaseModel

from src.enums.object_type import ObjectType


# TODO: move to the s3_storage.schemas file
class FileObjectUploaded(BaseModel):
    message: str
    bucket: ObjectType
    filename: str
