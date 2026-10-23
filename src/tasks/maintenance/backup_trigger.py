from datetime import date

import src.core as core
from celery import Task, shared_task
from src.enums import TaskScheduleStatus
from src.schemas.backup.schedule import ScheduledBackupFilters
from src.services import BackupSchedulerService


@shared_task(bind=True)
def backup_trigger(self: Task, *args, **kwargs) -> None:
    """
    This task is triggered 5 minutes before the actual backup is scheduled.
    Celery ETA is used to ensure the backup will run within 5 minutes.
    """

    db_gen = core.get_db()
    db = next(db_gen)

    backup_db_gen = core.get_backup_db()
    backup_db = next(backup_db_gen)

    try:
        service = BackupSchedulerService(db, backup_db)

        query = service.get_schedules_query(
            ScheduledBackupFilters(
                scheduled_from=date.today(),
                scheduled_to=date.today(),
                status=TaskScheduleStatus.QUEUED,
            )
        )
        schedule = query.first()

        if schedule is None:
            return

        service.schedule_backup_task_type(schedule)

    finally:
        backup_db_gen.close()
        db_gen.close()
