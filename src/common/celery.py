import logging
import uuid
from typing import Any, cast

from sqlalchemy.exc import NoResultFound
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

    try:
        task_ref = service.get_by_id(cast(uuid.UUID, task.request.id))

        if task_ref.status != status.value:
            task_ref.status = status.value

            db.commit()

    except NoResultFound:
        logging.warning(
            "Unable to find task db record when trying to update task status. Continuing task"
        )
