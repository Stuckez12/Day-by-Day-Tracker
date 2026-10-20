from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import NoResultFound

from src.core.permission_validator import PermissionValidator
from src.core.s3_storage import ObjectStorageDep, ObjectType
from src.enums.backup.backup_id_type import BackupIDType
from src.exc import (
    HTTP_EXC_BACKUP_FILENAME_PRESENT,
    HTTP_EXC_BACKUP_NOT_FOUND,
    HTTP_EXC_INVALID_BACKUP_ID_SPECIFICATION,
    HTTP_EXC_NO_BACKUP_FILENAME,
    HTTP_EXC_NO_BACKUP_METADATA,
    HTTP_EXC_UPLOAD_BACKUP_FILE,
)
from src.schemas import BackupSchema, TaskIDSchema
from src.services.dependencies import BackupServiceDep
from src.tasks import uploaded_backup_record_creation, verify_logical_backup

from .schedule import api as schedule_api


api = APIRouter(
    prefix="/backup",
    tags=["Backup"],
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)
api.include_router(schedule_api)


@api.get("/all", response_model=list[BackupSchema], status_code=status.HTTP_200_OK)
def get_all_backups(service: BackupServiceDep):
    return service.get_all()


@api.post("/upload", response_model=TaskIDSchema, status_code=status.HTTP_202_ACCEPTED)
async def upload_backup(object_storage: ObjectStorageDep, file: UploadFile):
    if file.filename is None:
        raise HTTP_EXC_NO_BACKUP_FILENAME

    file_exists = object_storage.file_exists(ObjectType.BACKUP, file.filename)

    if file_exists:
        raise HTTP_EXC_BACKUP_FILENAME_PRESENT

    try:
        file_data = object_storage.upload_file(
            file.file, ObjectType.BACKUP, file.filename
        )

        task: AsyncResult = uploaded_backup_record_creation.s(
            new_backup_file=file_data.filename
        ).apply_async()

        return TaskIDSchema(task_id=UUID(task.id))

    except Exception:
        raise HTTP_EXC_UPLOAD_BACKUP_FILE


@api.get("/{backup_id}", response_model=BackupSchema, status_code=status.HTTP_200_OK)
def get_backup(
    service: BackupServiceDep,
    backup_id: UUID,
    id_type: BackupIDType = Query(default=BackupIDType.BACKUP),
):
    match id_type:
        case BackupIDType.BACKUP:
            try:
                return service.get_by_backup_id(backup_id)

            except NoResultFound:
                raise HTTP_EXC_BACKUP_NOT_FOUND

        case BackupIDType.CELERY:
            try:
                return service.get_by_task_id(backup_id)

            except NoResultFound:
                raise HTTP_EXC_BACKUP_NOT_FOUND

        case _:
            raise HTTP_EXC_INVALID_BACKUP_ID_SPECIFICATION


@api.get(
    "/{backup_id}/download",
    response_model=list[BackupSchema],
    status_code=status.HTTP_200_OK,
)
def download_backup(
    service: BackupServiceDep, object_storage: ObjectStorageDep, backup_id: UUID
):
    try:
        backup = service.get_by_backup_id(backup_id)

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND

    if backup.meta is None:
        raise HTTP_EXC_NO_BACKUP_METADATA

    file_object = object_storage.download_file(ObjectType.BACKUP, backup.meta.zip_path)

    return StreamingResponse(
        file_object.file,
        media_type=file_object.file_type,
        headers={
            "Content-Disposition": f'attachment; filename="{backup.meta.zip_filename}"'
        },
    )


@api.patch(
    "/{backup_id}/verify", response_model=TaskIDSchema, status_code=status.HTTP_200_OK
)
def verify_backup_route(service: BackupServiceDep, backup_id: UUID):
    try:
        backup = service.get_by_backup_id(backup_id)

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND

    task: AsyncResult = verify_logical_backup.s(backup_id=backup.id).apply_async()

    return TaskIDSchema(task_id=UUID(task.id))
