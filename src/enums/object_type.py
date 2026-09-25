from enum import Enum


# TODO: Move into the s3_storage folder
class ObjectType(Enum):
    BACKUP = "backups"
    IMAGE = "images"
