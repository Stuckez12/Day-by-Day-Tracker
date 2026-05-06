import uuid

from celery import Task
from celery.result import AsyncResult
from sqlalchemy.orm import Session

from src.enums import TaskStatus
from src.models import TaskModel
from src.services.base import BaseDBService


class TaskService(BaseDBService[TaskModel]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=TaskModel)

    def register_task(self, task_id: uuid.UUID, name: str):
        record = TaskModel(task_id, name, TaskStatus.PENDING)

        self.db.add(record)
        self.db.commit()

        return record

    def get_by_id(self, task_id: uuid.UUID) -> TaskModel | None:
        return self.db.query(TaskModel).filter(TaskModel.task_id == task_id).first()

    def task_progress(self, task_ref: TaskModel):
        if task_ref.status != TaskStatus.RUNNING.value:
            if task_ref.status == TaskStatus.PENDING.value:
                raise ValueError("Task is waiting to be processed")

            raise ValueError("Task has finished processing")

        task = AsyncResult(str(task_ref.task_id))

        return {"status": task.state, "info": task.info}

    def filter_search(self):
        pass
