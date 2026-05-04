import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status

from src.common import TaskServiceDep
import src.tasks.task_management
from src.tasks import simulate_celery_task

api = APIRouter(prefix="/tasks", tags=["Task"])


@api.get("/", status_code=status.HTTP_200_OK)
def get_tasks(service: TaskServiceDep):

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Personnel does not exist"
    )


@api.get("/{task_id}", status_code=status.HTTP_200_OK)
def get_tasks(service: TaskServiceDep, task_id: uuid.UUID):
    task = service.get_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )

    return task


@api.get("/{task_id}/status", status_code=status.HTTP_200_OK)
def get_tasks(service: TaskServiceDep, task_id: uuid.UUID):
    task = service.get_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )

    return service.task_progress(task)


@api.post("/test-run", status_code=status.HTTP_200_OK)
def get_tasks(service: TaskServiceDep):
    import src.tasks.task_management

    task: AsyncResult = simulate_celery_task.delay()

    return {"task_id": task.id}
