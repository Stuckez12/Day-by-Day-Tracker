from pathlib import Path
from typing import cast
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import NoResultFound

from src.common import BackupServiceDep
from src.exc import (
    HTTP_EXC_BACKUP_NOT_FOUND,
    HTTP_EXC_NO_BACKUP_METADATA,
    HTTP_EXC_NO_VALID_BACKUP_ID,
)
from src.schemas import BackupSchema, TaskIDSchema
from src.settings import app_config
from src.tasks import verify_backup


api = APIRouter(prefix="/backup", tags=["Backup"])


@api.get("", response_model=BackupSchema, status_code=status.HTTP_200_OK)
def get_backup(
    service: BackupServiceDep,
    backup_id: UUID | None = Query(None),
    celery_id: UUID | None = Query(None),
):
    if backup_id is None and celery_id is None:
        raise HTTP_EXC_NO_VALID_BACKUP_ID

    if backup_id:
        try:
            return service.get_by_backup_id(backup_id)

        except NoResultFound:
            raise HTTP_EXC_BACKUP_NOT_FOUND

    try:
        return service.get_by_task_id(cast(UUID, celery_id))

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND


@api.get("/all", response_model=list[BackupSchema], status_code=status.HTTP_200_OK)
def get_all_backups(service: BackupServiceDep):
    return service.get_all()


@api.post("/upload", response_model=TaskIDSchema, status_code=status.HTTP_202_ACCEPTED)
async def upload_backup(service: BackupServiceDep, file: UploadFile):
    task_id = await service.upload_backup_file(file)

    return TaskIDSchema(task_id=task_id)


@api.get(
    "/{backup_id}/download",
    response_model=list[BackupSchema],
    status_code=status.HTTP_200_OK,
)
def download_backup(service: BackupServiceDep, backup_id: UUID):
    try:
        backup = service.get_by_backup_id(backup_id)

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND

    if backup.meta is None:
        raise HTTP_EXC_NO_BACKUP_METADATA

    return FileResponse(
        Path(f"{app_config.BACKUP_PATH}{backup.meta.zip_path}"),
        media_type="application/octet-stream",
        filename=backup.meta.zip_filename,
    )


@api.patch(
    "/{backup_id}/verify",
    response_model=TaskIDSchema,
    status_code=status.HTTP_200_OK,
)
def verify_backup_route(service: BackupServiceDep, backup_id: UUID):
    try:
        backup = service.get_by_backup_id(backup_id)

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND

    task: AsyncResult = verify_backup.s(backup_id=backup.id).apply_async()

    return TaskIDSchema(task_id=UUID(task.id))
