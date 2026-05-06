from celery import Task
from sqlalchemy.orm import Session
from typing import Any

from src.enums import TaskStatus
from src.services import TaskService


def update_task_state(
    task: Task,
    db: Session,
    status: TaskStatus = TaskStatus.RUNNING,
    metadata: dict[str, Any] = {},
):
    task.update_state(
        state=status.value,
        meta=metadata,
    )

    service = TaskService(db)
    task_ref = service.get_by_id(task.request.id)

    if task_ref.status != status.value:
        task_ref.status = status.value

        db.commit()
