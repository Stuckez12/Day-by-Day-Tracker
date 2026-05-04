import time
import logging
from celery import shared_task, Task

import src.tasks.task_management
from src.common import get_db
from src.common.celery import update_task_state
from src.enums import TaskStatus


@shared_task(bind=True)
def simulate_celery_task(self: Task) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    try:
        for i in range(100):
            time.sleep(1)
            logging.info(f"SIMULATE TASK STEP: {i}")
            update_task_state(self, db, TaskStatus.RUNNING, {"progress": i})

        return {"progress": 100}

    finally:
        db_gen.close()
