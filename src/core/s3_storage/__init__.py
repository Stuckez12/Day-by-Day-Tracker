from src.core.s3_storage.schemas import (
    FileObjectDownloadSchema,
    FileObjectMetadataSchema,
)
from src.core.s3_storage.service import (
    ObjectStorage,
    ObjectStorageDep,
    get_object_storage_service,
)
