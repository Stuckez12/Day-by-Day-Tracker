import subprocess

from celery import shared_task, Task
from datetime import datetime

import src.tasks.task_management
from src.common import get_db
from src.common.celery import update_task_state
from src.enums import TaskStatus
from src.models import BackupModel
from src.settings import app_config


@shared_task(bind=True)
def database_backup(self: Task) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    try:
        date = datetime.now().strftime("%Y-%b-%d")
        backup_file = f"{app_config.DATABASE_DB_NAME}-backup-{date}"

        file_path = f"{app_config.BACKUP_PATH}/{backup_file}.dump"

        command = [
            "pg_dump",
            "-h",
            app_config.DATABASE_HOST,
            "-p",
            str(app_config.DATABASE_PORT),
            "-U",
            app_config.DATABASE_USERNAME,
            "-F",
            "p",
            "-f",
            file_path,
            app_config.DATABASE_DB_NAME,
        ]
        env = {"PGPASSWORD": app_config.DATABASE_PASSWORD}

        update_task_state(
            self,
            db,
            metadata={"stage": f"Creating Database Backup: {file_path}"},
        )

        try:
            subprocess.run(command, env=env, check=True, capture_output=True, text=True)

        except subprocess.CalledProcessError as e:
            print("RETURN CODE:", e.returncode)
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            raise SystemError("Unable to create database backup")

        update_task_state(self, db, metadata={"stage": "Recording Backup"})

        date_obj = datetime.strptime(date, "%Y-%b-%d")
        backup = BackupModel(backup_file, date_obj, file_path)

        db.add(backup)
        db.commit()
        db.refresh(backup)

        return backup

    finally:
        db_gen.close()
