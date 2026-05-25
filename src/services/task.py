import uuid
from datetime import timedelta

from celery.result import AsyncResult
from sqlalchemy.orm import Session

from src.enums import TaskStatus
from src.models import TaskModel
from src.schemas import TaskPaginated
from src.services.base import BaseDBService


class TaskService(BaseDBService[TaskModel]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=TaskModel)

    def register_task(self, task_id: uuid.UUID, name: str):
        record = TaskModel(task_id, name, TaskStatus.PENDING)

        self.db.add(record)
        self.db.commit()

        return record

    def get_by_id(self, task_id: uuid.UUID) -> TaskModel | None:  # type: ignore
        return self.db.query(TaskModel).filter(TaskModel.task_id == task_id).first()

    def task_progress(self, task_ref: TaskModel):
        if task_ref.status != TaskStatus.RUNNING.value:
            if task_ref.status == TaskStatus.PENDING.value:
                raise ValueError("Task is waiting to be processed")

            raise ValueError("Task has finished processing")

        task: AsyncResult = AsyncResult(str(task_ref.task_id))

        return {"status": task.state, "info": task.info}

    def get_paginated_query(self, filters: TaskPaginated):
        query = self.db.query(TaskModel)

        if filters.task_id is not None:
            query = query.filter(TaskModel.task_id == filters.task_id)

        if filters.name is not None:
            query = query.filter(TaskModel.name.ilike(f"%{filters.name}%"))

        if filters.task_status is not None:
            statuses = [status.value for status in filters.task_status]
            query = query.filter(TaskModel.status.in_(statuses))

        if filters.min_retries is not None:
            query = query.filter(TaskModel.retries >= filters.min_retries)

        if filters.max_retries is not None:
            query = query.filter(TaskModel.retries <= filters.max_retries)

        if filters.started_at is not None:
            query = query.filter(TaskModel.started_at >= filters.started_at)

        if filters.ended_at is not None:
            query = query.filter(TaskModel.ended_at <= filters.ended_at)

        if filters.duration is not None:
            time_dur = timedelta(seconds=filters.duration)
            query = query.filter(TaskModel.ended_at - TaskModel.started_at >= time_dur)

        return query
