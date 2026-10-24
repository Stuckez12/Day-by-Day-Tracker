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
        "backup-scheduler": {
            "task": "src.tasks.maintenance.backup_scheduler.backup_scheduler",
            "schedule": crontab(
                month_of_year="*/3", day_of_month=1, hour=23, minute=55
            ),
        },
        "trigger-scheduled-backups": {
            "task": "src.tasks.maintenance.backup_trigger.backup_trigger",
            "schedule": crontab(hour=23, minute=56),
        },
    }

    return worker
