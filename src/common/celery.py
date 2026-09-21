import logging
import uuid
from typing import Any, cast

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from celery import Task
from src.enums import TaskStatus
from src.services import TaskService


# TODO: Maybe if we get more tasks with many more steps, we explore a new way of defining backup
# steps using a dict of task enum states and backup stage schemas explaining each step in general
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
        task_ref = service.get_by_task_id(cast(uuid.UUID, task.request.id))

        if task_ref.status != status.value:
            task_ref.status = status.value

            db.commit()

        if metadata.get("stage", None) is not None:
            logging.info(f"Stage: {metadata.get('stage', 'No stage found')}")

    except NoResultFound:
        logging.warning(
            "Unable to find task db record when trying to update task status. Continuing task"
        )
