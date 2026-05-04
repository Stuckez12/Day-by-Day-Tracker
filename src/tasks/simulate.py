import time
from celery import shared_task, Task


@shared_task(bind=True)
def simulate_celery_task(self: Task):
    for i in range(100):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={"progress": i},
        )

    return {"progress": 100}
