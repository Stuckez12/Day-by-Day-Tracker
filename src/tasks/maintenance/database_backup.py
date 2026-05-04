import subprocess
import logging

from celery import shared_task, Task
from datetime import datetime

import src.tasks.task_management
from src.common import get_db
from src.common.celery import update_task_state
from src.enums import TaskStatus
from src.settings import app_config


@shared_task(bind=True)
def database_backup(self: Task) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    try:
        backup_file = f"{app_config.DATABASE_DB_NAME}-backup-{datetime.now().strftime('%Y-%b-%d')}.dump"

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
            backup_file,
            app_config.DATABASE_DB_NAME,
        ]
        env = {"PGPASSWORD": app_config.DATABASE_PASSWORD}

        update_task_state(
            self,
            db,
            TaskStatus.RUNNING,
            {"stage": f"Creating Database Backup: {backup_file}"},
        )

        subprocess.run(command, env=env, check=True)

        update_task_state(
            self, db, TaskStatus.RUNNING, {"stage": "Backup Successfully Created"}
        )

    finally:
        db_gen.close()
