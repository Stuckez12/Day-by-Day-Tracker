import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import cast

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database

from src.common import utcnow
from src.core.database.recreate_db import recreate_database
from src.core.s3_storage import ObjectStorage
from src.models import BackupModel
from src.models.ranking import RankerModel
from src.schemas import (
    MetadataChecksum,
    MetadataDateRange,
    MetadataFiles,
)
from src.settings import app_config
from src.workflows.backup.base import BaseBackupWorkflow


class LogicalBackupWorkflow(BaseBackupWorkflow):
    def __init__(
        self,
        *,
        db: Session,
        backup_db: Session,
        backup_record: BackupModel,
        object_storage: ObjectStorage,
    ) -> None:
        super().__init__(
            db=db,
            backup_db=backup_db,
            backup_record=backup_record,
            object_storage=object_storage,
        )

    # ------------------------ DB Backup ----------------------- #

    def create_logical_database_backup(self) -> None:
        date = datetime.now().strftime("%Y-%b-%d")
        backup_file_name = f"{app_config.DATABASE_DB_NAME}-backup-{date}"

        file_path = self.temp_backup_path / f"{backup_file_name}.dump"

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
            str(file_path),
            app_config.DATABASE_DB_NAME,
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = app_config.DATABASE_PASSWORD

        try:
            subprocess.run(command, env=env, check=True, capture_output=True, text=True)

            self.backup_file_path = file_path
            algorithm, checksum = self._generate_checksum(file_path)

            self.metadata_files.append(
                MetadataFiles(
                    type="backup",
                    name=Path(file_path).name,
                    size_bytes=Path(file_path).stat().st_size,
                    checksum=MetadataChecksum(
                        algorithm=algorithm,
                        value=checksum,
                        verified=True,
                        last_verified=utcnow(),
                    ),
                )
            )

            self.metadata_tool = self._get_pg_dump_metadata_tool()

            start, end = self._get_database_date_range()
            self.metadata_date_range = MetadataDateRange(start=start, end=end)

        except subprocess.CalledProcessError as e:
            raise SystemError(f"""
Unable to create database backup

RETURN CODE: {e.returncode}
STDOUT: {e.stdout}
STDERR: {e.stderr}
""")

    def _restore_backup_in_database(self, database_name: str) -> None:
        if self.backup_file_path is None:
            raise ValueError("Backup file path not set")

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
            self.backup_file_path,
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

    def verify_backup_file(self) -> None:
        test_database_name = "restore_backup_test"
        temp_db_url = recreate_database(test_database_name)

        try:
            self._restore_backup_in_database(test_database_name)

        finally:
            drop_database(temp_db_url)

    # ----------------------- File Backup ---------------------- #

    def create_object_folder_backup(self) -> None:
        """Only for object storage files within the rustfs container/dedicated ssd directory"""
        pass

    # ------------------------ Metadata ------------------------ #

    def _get_database_date_range(self) -> tuple[datetime, datetime]:
        min_date, max_date = (
            self.db.query(
                func.min(RankerModel.created_at),
                func.max(RankerModel.updated_at),
            )
            .select_from(RankerModel)
            .one()
        )

        return cast(datetime, min_date), cast(datetime, max_date)
