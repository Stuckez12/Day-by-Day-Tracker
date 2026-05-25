import logging
import uuid
from typing import Any, cast

from sqlalchemy.orm import Session

from celery import Task
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
    task_ref = service.get_by_id(cast(uuid.UUID, task.request.id))

    try:
        if task_ref is None:
            raise ValueError("Task not found")

        if task_ref.status != status.value:
            task_ref.status = status.value

            db.commit()

    except:
        logging.warning(
            "Unable to find task db record when trying to update task status. Continuing task"
        )
