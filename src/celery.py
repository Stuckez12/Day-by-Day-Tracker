from celery import Celery

from src.settings import app_config


def create_worker():
    worker = Celery("tasks", broker=app_config.CELERY_URL)
    # worker = Celery("tasks", broker=app_config.REDIS_URL + "/0")
    worker.config_from_object(app_config, namespace="CELERY")

    worker.autodiscover_tasks(
        packages=["src"],
    )

    return worker
