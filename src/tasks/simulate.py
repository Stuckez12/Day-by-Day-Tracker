import logging
import time

import src.core as core
from celery import Task, shared_task
from src.common.celery import update_task_state


@shared_task(bind=True)
def simulate_celery_task(self: Task, *args, **kwargs) -> dict:
    db_gen = core.get_db()
    db = next(db_gen)

    try:
        for i in range(20):
            time.sleep(0.1)
            logging.info(f"SIMULATE TASK STEP: {i}")
            update_task_state(self, db, metadata={"progress": i})

        return {"progress": 100}

    finally:
        db_gen.close()
