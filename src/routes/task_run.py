from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Request, status

import src.tasks.task_management  # noqa
from src.enums import BackupTriggerMethod
from src.tasks import database_logical_backup, simulate_celery_task, verify_backup


api = APIRouter(prefix="/execute/task", tags=["Execute Task"])


@api.get("/simulate", status_code=status.HTTP_200_OK)
def run_task_simulation(_: Request):
    task: AsyncResult = simulate_celery_task.delay()

    return task.get()


@api.get("/database-backup", status_code=status.HTTP_200_OK)
def run_database_logical_backup(_: Request):
    task: AsyncResult = database_logical_backup.delay(
        trigger=BackupTriggerMethod.MANUAL.value
    )

    return task.get()


@api.get("/verify-backup", status_code=status.HTTP_200_OK)
def run_verify_backup(backup_id: UUID):
    task: AsyncResult = verify_backup.delay(backup_id=backup_id)

    return task.get()
