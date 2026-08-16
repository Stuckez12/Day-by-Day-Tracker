from pathlib import Path
from typing import cast
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import NoResultFound

from src.common import BackupServiceDep
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either a backup id or celery task id",
        )

    if backup_id:
        try:
            return service.get_by_backup_id(backup_id)

        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Backup does not exist"
            )

    try:
        return service.get_by_task_id(cast(UUID, celery_id))

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Backup does not exist"
        )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Backup does not exist"
        )

    if backup.meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup does not have the required metadata",
        )

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Backup does not exist"
        )

    task: AsyncResult = verify_backup.s(backup_id=backup.id).apply_async()

    return TaskIDSchema(task_id=UUID(task.id))
