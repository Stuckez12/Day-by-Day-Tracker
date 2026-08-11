import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import cast
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy import func, text
from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database

from src.common.recreate_db import recreate_database
from src.models import BackupModel
from src.models.ranking import RankerModel
from src.schemas import (
    BackupCreate,
    Metadata,
    MetadataChecksum,
    MetadataData,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.services.base import BaseDBService
from src.settings import app_config


class BackupService(BaseDBService):
    temp_file_path: str = f"{app_config.BACKUP_PATH}/temp"
    temp_restore_path: str = f"{app_config.BACKUP_PATH}/restore"

    def __init__(self, db: Session, backup_db: Session) -> None:
        super().__init__(db=db, model=BackupModel)

        self.backup_db = backup_db

    def create(self, data: BackupCreate) -> BackupModel:
        backup = BackupModel(**data.model_dump())

        self.backup_db.add(backup)
        self.backup_db.commit()
        self.backup_db.refresh(backup)

        return backup

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

    def sha256_file(self, file_path: str) -> str:
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def generate_checksum_file(self, file_path: str) -> str:
        checksun_value = self.sha256_file(file_path)

        checksum_file = f"{self.temp_file_path}/checksum.hash"

        with open(checksum_file, "w+") as f:
            f.write(checksun_value)

        return checksum_file

    def validate_checksum(self, metadata: Metadata):
        backup_file_data = metadata.get_file_type_data("backup")
        checksum_file_data = metadata.get_file_type_data("checksum")

        if backup_file_data is None or checksum_file_data is None:
            raise FileNotFoundError("Backup/checksum file not present in metadata")

        with open(f"{self.temp_restore_path}/{checksum_file_data.name}", "r") as f:
            data = f.readlines()
            assert len(data) == 1, "Corrupted checksum file. Cannot restore"

            checksum_value = data[0]
            backup_checksum = self.sha256_file(
                f"{self.temp_restore_path}/{backup_file_data.name}"
            )

            if checksum_value != backup_checksum:
                raise ValueError("Backup file corrupted. Checksum value does not match")

    def create_metadata(
        self, backup_record: BackupModel, backup_file: str, checksum_file: str
    ) -> Metadata:
        min_date, max_date = (
            self.db.query(
                func.min(RankerModel.created_at),
                func.max(RankerModel.updated_at),
            )
            .select_from(RankerModel)
            .one()
        )

        alembic_version = self.db.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar()

        files = [
            MetadataFiles(
                name=Path(backup_file).name,
                type="backup",
                size_bytes=Path(backup_file).stat().st_size,
            ),
            MetadataFiles(
                name=Path(checksum_file).name,
                type="checksum",
                size_bytes=Path(checksum_file).stat().st_size,
            ),
        ]

        return Metadata(
            schema_version=1,
            backup_id=str(backup_record.id),
            backup_type=backup_record.backup_type,
            created_at=backup_record.created_at,
            database_alembic_version=cast(str, alembic_version),
            app_version=app_config.APP_VERSION,
            checksum=MetadataChecksum(
                algorithm="sha256", file_name=Path(checksum_file).name
            ),
            tool=MetadataTool(
                name="pg_dump",
                version=subprocess.check_output(["pg_dump", "--version"])
                .decode()
                .strip(),
            ),
            data=MetadataData(
                date_range=MetadataDateRange(start=min_date, end=max_date),
            ),
            files=files,
        )

    def create_metadata_file(self, metadata: Metadata) -> str:
        metadata_file_path = f"{self.temp_file_path}/metadata.json"

        with open(metadata_file_path, "w+") as f:
            f.write(metadata.model_dump_json())

        return metadata_file_path

    def zip_folder(self, zip_destination: str, files: list[str]):
        with ZipFile(zip_destination, "w", compression=ZIP_DEFLATED) as zf:
            for file in files:
                path = Path(file)
                zf.write(path, arcname=path.name)

    def unzip_folder(self, zip_file: str):
        zip_path = Path(f"{app_config.BACKUP_PATH}/{zip_file}")

        with ZipFile(zip_path, "r") as zf:
            zf.extractall(self.temp_restore_path)
