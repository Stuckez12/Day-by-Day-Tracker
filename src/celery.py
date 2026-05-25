from celery.schedules import crontab

from celery import Celery
from src.settings import app_config


def create_worker():
    worker = Celery(
        "tasks", broker=app_config.CELERY_URL, result_backend=app_config.CELERY_URL
    )
    worker.config_from_object(app_config, namespace="CELERY")
    worker.set_default()
    worker.autodiscover_tasks(
        packages=["src"],
    )

    # Schedules
    worker.conf.update(
        timezone="UTC",
        enable_utc=True,
    )
    worker.conf.beat_schedule = {
        "weekly-database-backup": {
            "task": "src.tasks.maintenance.database_backup.database_backup",
            "schedule": crontab(day_of_week="mon", hour=3, minute=0),
        },
    }

    return worker
