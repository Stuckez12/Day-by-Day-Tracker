import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import NoResultFound

from src.common import TaskServiceDep
from src.enums import TaskStatus
from src.schemas import TaskPaginated, TaskSchema


api = APIRouter(prefix="/task", tags=["Task"])


@api.get("/paginated", status_code=status.HTTP_200_OK, response_model=Page[TaskSchema])
def get_tasks_paginated(
    service: TaskServiceDep,
    params: Params = Depends(),
    task_id: str = Query(None),
    name: str = Query(None),
    task_status: list[TaskStatus] = Query(None),
    min_retries: int = Query(None),
    max_retries: int = Query(None),
    started_at: datetime = Query(None),
    ended_at: datetime = Query(None),
    duration: int = Query(None),
):
    filters = TaskPaginated(
        task_id=task_id,
        name=name,
        task_status=task_status,
        min_retries=min_retries,
        max_retries=max_retries,
        started_at=started_at,
        ended_at=ended_at,
        duration=duration,
    )

    query = service.get_paginated_query(filters)

    return paginate(query, params)


@api.get("/", status_code=status.HTTP_200_OK, response_model=TaskSchema)
def get_task(service: TaskServiceDep, task_id: uuid.UUID = Query(...)):
    try:
        task = service.get_by_task_id(task_id)

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )

    return task


@api.get("/{task_id}/status", status_code=status.HTTP_200_OK)
def get_task_status(service: TaskServiceDep, task_id: uuid.UUID):
    try:
        task = service.get_by_task_id(task_id)

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
        )

    return service.task_progress(task)
