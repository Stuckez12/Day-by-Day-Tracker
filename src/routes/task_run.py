from celery.result import AsyncResult
from fastapi import APIRouter, Request, status

from src.tasks import database_backup


api = APIRouter(prefix="/execute/task", tags=["Execute Task"])


@api.get("/database-backup", status_code=status.HTTP_200_OK)
def execute_task_simulation(_: Request):
    task: AsyncResult = database_backup.delay()

    return task.get()
