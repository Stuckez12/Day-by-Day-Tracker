import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import cast
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.common import utcnow
from src.core.s3_storage import ObjectStorage
from src.enums import BackupType, ObjectType
from src.models import BackupModel, MetaModel
from src.schemas import (
    Metadata,
    MetadataData,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.settings import app_config
from src.utils import delete_folder, sha256_file


class BaseBackupWorkflow:
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
        temp_path = app_config.TEMPORARY_PATH + "/backup"

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

        # Boolean guards
        self.backup_uploaded = False
        self.extracted_zip = False

    # ------------------------ DB Backup ----------------------- #

    def _generate_checksum(self, file_path: Path) -> tuple[str, str]:
        checksum = sha256_file(file_path)

        return "sha256", checksum

    def update_verification_metadata_record(self, verified: bool = True):
        if self.backup_record.meta is None:
            raise ValueError("Backup record does not have any attached metadata")

        self.backup_record.meta.verified = verified
        self.backup_record.meta.last_verified = utcnow().replace(tzinfo=None)

        self.backup_db.flush()

    # ----------------------- File Backup ---------------------- #

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

    def retrieve_metadata_from_file(self):
        if not self.extracted_zip:
            raise ValueError("ZIP file not extracted")

        self.metadata_file_path = self.temp_backup_path / "metadata.json"

        with open(self.metadata_file_path, "rb") as file:
            schema = json.load(file)

        self.metadata = Metadata.model_validate(
            {
                "backup_id": str(self.backup_record.id),
                **schema,
            }
        )

        for file in self.metadata.files:
            if file.type == "backup":
                self.backup_file_path = self.temp_backup_path / file.name

                break

    def validate_backup_type(self, backup_type: BackupType):
        if self.metadata is None:
            raise ValueError("Metadata not set")

        if self.metadata.backup_type != backup_type:
            raise ValueError("Provided backup type is incompatible")

    def validate_metadata_checksums(self):
        if self.metadata is None:
            raise ValueError("Metadata not set")

        for file in self.metadata.files:
            file_path = self.temp_backup_path / file.name

            _, checksum = self._generate_checksum(file_path)

            if checksum != file.checksum.value:
                raise ValueError(
                    f"Specified file '{file.name}' corrupted. Checksum does not match"
                )

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

    def retrieve_zip_file(self) -> None:
        if self.backup_record.meta is None:
            raise ValueError("Backup record does not have any attached metadata")

        file_data = self.object_storage.download_file(
            ObjectType.BACKUP, self.backup_record.meta.zip_path
        )

        self.zipped_backup_file_path = (
            self.temp_backup_path / self.backup_record.meta.zip_filename
        )

        with open(self.zipped_backup_file_path, "wb") as file:
            shutil.copyfileobj(file_data.file, file)

        self._extract_zip_file()

    def _extract_zip_file(self) -> None:
        if self.zipped_backup_file_path is None:
            raise ValueError("Zipped file path not set")

        with ZipFile(self.zipped_backup_file_path, "r") as zf:
            zf.extractall(self.temp_backup_path)

        self.extracted_zip = True

    def retrieve_downloaded_zip_file(self, new_backup_path: str) -> None:
        file_data = self.object_storage.download_file(
            ObjectType.BACKUP, new_backup_path
        )

        self.zipped_backup_file_path = self.temp_backup_path / new_backup_path
        self.backup_uploaded = True

        with open(self.zipped_backup_file_path, "wb") as file:
            shutil.copyfileobj(file_data.file, file)

        self._extract_zip_file()

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
        self.backup_db.flush([model])

    def cleanup(self) -> None:
        try:
            delete_folder(self.temp_backup_path)

        except FileNotFoundError:
            # What we expect to happen
            pass

        except FileExistsError:
            logging.error("Failed to clean up backup workflow temp files")

        except Exception:
            logging.error(
                "Unknown error whilst trying to clean up BackupWorkflow temp folder"
            )
