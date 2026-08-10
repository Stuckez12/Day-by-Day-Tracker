from celery import Task, shared_task
from src.common import get_backup_db, get_db
from src.common.celery import update_task_state
from src.services import BackupService


@shared_task(bind=True)
def database_backup(self: Task, *args, **kwargs) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    backup_db_gen = get_backup_db()
    backup_db = next(backup_db_gen)

    service = BackupService(db=db, backup_db=backup_db)

    try:
        update_task_state(
            self,
            db,
            metadata={"stage": "Creating Database Backup"},
        )

        backup_file = service.create_logical_backup()

        update_task_state(self, db, metadata={"stage": "Verifying Backup"})

        service.verify_backup_restoration(backup_file)

        return {}

    finally:
        backup_db_gen.close()
        db_gen.close()
