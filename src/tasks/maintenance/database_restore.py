import subprocess

from celery import shared_task, Task
from sqlalchemy_utils import database_exists, drop_database

import src.tasks.task_management
from src.common import get_db
from src.common.celery import update_task_state
from src.services import BackupService
from src.settings import app_config


@shared_task(bind=True)
def database_restore(self: Task, backup_id: str) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    try:
        update_task_state(self, db, metadata={"stage": "Verifying Backup"})

        service = BackupService(db)
        backup = service.get_by_id(backup_id)

        if backup is None:
            raise ValueError("Backup does not exist within the current database")

        print("Found backup")

        update_task_state(self, db, metadata={"stage": "Importing Database Backup"})

        restore_command = [
            "psql",
            "-h",
            app_config.DATABASE_HOST,
            "-p",
            str(app_config.DATABASE_PORT),
            "-U",
            app_config.DATABASE_USERNAME,
            "-d",
            app_config.DATABASE_DB_NAME,
            "-f",
            backup.file_path,
        ]
        env = {"PGPASSWORD": app_config.DATABASE_PASSWORD}

        try:
            print("importing")
            subprocess.run(restore_command, env=env, check=True)

        except subprocess.CalledProcessError as e:
            print("RETURN CODE:", e.returncode)
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            raise SystemError("Unable to import database backup")

        print("DONE")

        return None

    finally:
        db_gen.close()
