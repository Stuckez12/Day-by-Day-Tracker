import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import cast
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy import func, text
from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database

from src.common import utcnow
from src.core.database import recreate_database
from src.core.s3_storage import ObjectStorage
from src.enums import BackupType
from src.enums.object_type import ObjectType
from src.models import BackupModel
from src.models.backup.meta import MetaModel
from src.models.ranking import RankerModel
from src.schemas import (
    Metadata,
    MetadataChecksum,
    MetadataData,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.settings import app_config
from src.utils import sha256_file


class BackupWorkflow:
    temp_backup_path: Path

    backup_file_path: Path | None = None
    zipped_backup_file_path: Path | None = None

    # Metadata
    metadata: Metadata | None = None
    metadata_file_path: Path | None = None

    metadata_files: list[MetadataFiles] = []
    metadata_tool: MetadataTool | None = None
    metadata_date_range: MetadataDateRange | None = None

    def __init__(
        self,
        *,
        db: Session,
        backup_db: Session,
        backup_record: BackupModel,
        object_storage: ObjectStorage,
    ) -> None:
        self.db = db
        self.backup_db = backup_db
        self.backup_record = backup_record
        self.object_storage = object_storage

        # File paths
        temp_path = app_config.TEMPORARY_PATH + "/temp"

        self.temp_backup_path = Path(temp_path)
        self.temp_backup_path.mkdir(exist_ok=True)

        self.backup_file_path: Path | None = None
        self.zipped_backup_file_path: Path | None = None

        # Metadata
        self.metadata: Metadata | None = None
        self.metadata_file_path: Path | None = None

        self.metadata_files: list[MetadataFiles] = []
        self.metadata_tool: MetadataTool | None = None
        self.metadata_date_range: MetadataDateRange | None = None

        # Is backup uploaded
        self.backup_uploaded = False

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

    def verify_backup_file(self) -> None:
        test_database_name = "restore_backup_test"
        temp_db_url = recreate_database(test_database_name)

        try:
            self._restore_backup_in_database(test_database_name)

        finally:
            drop_database(temp_db_url)

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

    def _generate_checksum(self, file_path: Path) -> tuple[str, str]:
        checksum = sha256_file(file_path)

        return "sha256", checksum

    # ----------------------- File Backup ---------------------- #

    def create_object_folder_backup(self) -> None:
        """Only for object storage files within the rustfs container/dedicated ssd directory"""
        pass

    # ------------------------ Metadata ------------------------ #

    def generate_metadata(self, backup_type: BackupType):
        if self.metadata_tool is None:
            raise ValueError("Backup tool used not set")

        if self.metadata_date_range is None:
            raise ValueError("Backup date range not set")

        self.metadata = Metadata(
            backup_id=str(self.backup_record.id),
            backup_type=backup_type,
            created_at=utcnow(),
            database_alembic_version=self._current_alembic_version(),
            tool=self.metadata_tool,
            files=self.metadata_files,
            data=MetadataData(date_range=self.metadata_date_range),
        )

        self._create_metadata_file()

    def _create_metadata_file(self) -> None:
        if self.backup_file_path is None:
            raise ValueError("Backup file path not set")

        if self.metadata is None:
            raise ValueError("Metadata not set")

        meta_json = self.metadata.model_dump_json(exclude={"backup_id"})

        self.metadata_file_path = self.temp_backup_path / "metadata.json"

        with open(self.metadata_file_path, "w+") as f:
            f.write(meta_json)

    def _current_alembic_version(self) -> str:
        version = self.db.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar()

        return cast(str, version)

    def _get_pg_dump_metadata_tool(self) -> MetadataTool:
        return MetadataTool(
            name="pg_dump",
            version=subprocess.check_output(["pg_dump", "--version"]).decode().strip(),
        )

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

    # ------------------------ ZIP File ------------------------ #

    def zip_all_backup_files(self) -> None:
        if self.backup_file_path is None:
            raise ValueError("Backup file path not set")

        if self.metadata is None:
            raise ValueError("Metadata not set")

        if self.metadata_file_path is None:
            raise ValueError("Metadata file path not set")

        backup_files: list[Path] = [
            self.backup_file_path,
            self.metadata_file_path,
        ]

        backup_created_at = self.metadata.created_at.strftime("%Y%m%d%H%M%S")
        self.zipped_backup_file_path = (
            self.temp_backup_path / f"{backup_created_at}-tracker-backup.zip"
        )

        with ZipFile(self.zipped_backup_file_path, "w", compression=ZIP_DEFLATED) as zf:
            for file in backup_files:
                zf.write(file, arcname=file.name)

    def upload_zip_to_object_storage(self) -> None:
        if self.zipped_backup_file_path is None:
            raise ValueError("Zipped file path not set")

        with open(self.zipped_backup_file_path, "rb") as file:
            filename = self.zipped_backup_file_path.name
            self.object_storage.upload_file(file, ObjectType.BACKUP, filename)

            self.backup_uploaded = True

    # ------------------------- Utils -------------------------- #

    def record_backup_into_database(self) -> None:
        if self.metadata is None:
            raise ValueError("Metadata not set")

        if self.zipped_backup_file_path is None:
            raise ValueError("Zipped file path not set")

        if not self.backup_uploaded:
            raise ValueError(
                "Backup must be uploaded into the object storage container"
            )

        file_object = self.object_storage.file_metadata(
            ObjectType.BACKUP, self.zipped_backup_file_path.name
        )

        model = MetaModel(metadata_schema=self.metadata, zipped_metadata=file_object)

        self.backup_db.add(model)
        self.backup_db.commit()
