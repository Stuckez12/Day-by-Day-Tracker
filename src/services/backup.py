import os
import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database

from src.common.recreate_db import recreate_database
from src.models import BackupModel
from src.services.base import BaseDBService
from src.settings import app_config


class BackupService(BaseDBService):
    temp_file_path: str = f"{app_config.BACKUP_PATH}/temp"
    temp_file_path: str = f"{app_config.BACKUP_PATH}/restore"

    def __init__(self, db: Session, backup_db: Session) -> None:
        super().__init__(db=db, model=BackupModel)

        self.backup_db = backup_db

    def create_logical_backup(self):
        date = datetime.now().strftime("%Y-%b-%d")
        backup_file_name = f"{app_config.DATABASE_DB_NAME}-backup-{date}"
        file_path = f"{self.temp_file_path}/{backup_file_name}.dump"

        Path(self.temp_file_path).mkdir(parents=True, exist_ok=True)

        command = [
            "pg_dump",
            "--clean",
            "--if-exists",
            "-h",
            app_config.DATABASE_HOST,
            "-p",
            str(app_config.DATABASE_PORT),
            "-U",
            app_config.DATABASE_USERNAME,
            "-F",
            "c",
            "-f",
            file_path,
            app_config.DATABASE_DB_NAME,
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = app_config.DATABASE_PASSWORD

        try:
            subprocess.run(command, env=env, check=True, capture_output=True, text=True)  # type: ignore[arg-type]

            return file_path

        except subprocess.CalledProcessError as e:
            raise SystemError(f"""
Unable to create database backup

RETURN CODE: {e.returncode}
STDOUT: {e.stdout}
STDERR: {e.stderr}
""")

    def verify_backup_restoration(self, file_path: str):
        test_database_name = "restore_backup_test"
        temp_db_url = recreate_database(test_database_name)

        try:
            self.restore_backup_in_database(file_path, test_database_name)

        finally:
            drop_database(temp_db_url)

    def restore_backup_in_database(self, file_path: str, database_name: str):
        command = [
            "pg_restore",
            "--clean",
            "--if-exists",
            "-h",
            app_config.DATABASE_HOST,
            "-p",
            str(app_config.DATABASE_PORT),
            "-U",
            app_config.DATABASE_USERNAME,
            "-d",
            database_name,
            file_path,
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = app_config.DATABASE_PASSWORD

        try:
            subprocess.run(
                command,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

        except subprocess.CalledProcessError as e:
            raise SystemError(f"""
Unable to restore database backup

RETURN CODE: {e.returncode}
STDOUT: {e.stdout}
STDERR: {e.stderr}
""")

    def apply_checksum(self):
        pass

    def validate_checksum(self):
        pass
