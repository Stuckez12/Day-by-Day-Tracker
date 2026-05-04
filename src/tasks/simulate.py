import time
import logging
from celery import shared_task, Task

from src.enums import TaskStatus
import src.tasks.task_management


@shared_task(bind=True)
def simulate_celery_task(self: Task) -> dict:
    for i in range(100):
        time.sleep(1)
        logging.info(f"SIMULATE TASK STEP: {i}")
        self.update_state(
            state=TaskStatus.RUNNING.value,
            meta={"progress": i},
        )

    return {"progress": 100}
