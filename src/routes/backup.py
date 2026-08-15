from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, UploadFile, status

from src.common import BackupServiceDep
from src.schemas import BackupSchema, DetailSchema, TaskIDSchema


api = APIRouter(prefix="/backups", tags=["Backup"])


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
        return service.get_by_backup_id(backup_id)

    if celery_id:
        return service.get_by_task_id(celery_id)


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
def download_backup(service: BackupServiceDep):
    pass


@api.patch(
    "/{backup_id}/verify",
    response_model=DetailSchema,
    status_code=status.HTTP_200_OK,
)
def verify_backup(service: BackupServiceDep):
    pass
