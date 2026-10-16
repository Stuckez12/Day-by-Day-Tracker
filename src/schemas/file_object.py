from pydantic import BaseModel

from src.enums import ObjectType


# TODO: move to the s3_storage.schemas file
class FileObjectUploaded(BaseModel):
    message: str
    bucket: ObjectType
    filename: str
