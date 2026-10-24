import src.core as core
from celery import Task, shared_task
from src.services import BackupSchedulerService


@shared_task(bind=True)
def backup_scheduler(self: Task, *args, **kwargs):
    db_gen = core.get_db()
    db = next(db_gen)

    backup_db_gen = core.get_backup_db()
    backup_db = next(backup_db_gen)

    try:
        service = BackupSchedulerService(db, backup_db)

        service.generate_schedules()

    finally:
        backup_db_gen.close()
        db_gen.close()
