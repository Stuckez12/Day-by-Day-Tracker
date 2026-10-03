import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database

from src.common.utils import utcnow
from src.core.database import temporary_db_session
from src.core.database.recreate_db import recreate_database
from src.core.s3_storage import ObjectStorage
from src.models import BackupModel, TaskModel
from src.models.base import Base
from src.schemas import DateRangeRequest
from src.schemas.backup import (
    MetadataChecksum,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.workflows.backup.base import BaseBackupWorkflow


NO_BACKUP_TABLES = [TaskModel]
BACKUP_TABLE_ORDER = []


class RangedBackupWorkflow(BaseBackupWorkflow):
    def __init__(
        self,
        *,
        db: Session,
        backup_db: Session,
        backup_record: BackupModel,
        object_storage: ObjectStorage,
        date_range: DateRangeRequest,
    ) -> None:
        super().__init__(
            db=db,
            backup_db=backup_db,
            backup_record=backup_record,
            object_storage=object_storage,
        )

        self.start_date = date_range.min_date
        self.end_date = date_range.max_date

        self.metadata_date_range = MetadataDateRange(
            start=datetime.combine(date_range.min_date, datetime.min.time()),
            end=datetime.combine(date_range.max_date, datetime.min.time()),
        )

    # ------------------------ DB Backup ----------------------- #

    def create_ranged_backup(self) -> None:
        result = {}
        restricted_table_names = [table.__tablename__ for table in NO_BACKUP_TABLES]

        self.metadata_date_range = cast(MetadataDateRange, self.metadata_date_range)

        for table in Base.metadata.sorted_tables:
            if table.fullname in restricted_table_names:
                continue

            if "updated_at" not in table.c:
                continue

            stmt = select(table).where(
                table.c.updated_at >= self.metadata_date_range.start,
                table.c.updated_at < self.metadata_date_range.end + timedelta(days=1),
            )

            rows = self.db.execute(stmt).mappings().all()
            result[table.name] = [dict(row) for row in rows]

        self.backup_file_path = self.temp_backup_path / "dump.json"
        self._write_to_json_file(self.backup_file_path, result)

        algorithm, checksum = self._generate_checksum(self.backup_file_path)

        self.metadata_tool = MetadataTool(name="dbdt_json_collector", version="1")
        self.metadata_files.append(
            MetadataFiles(
                type="backup",
                name=Path(self.backup_file_path).name,
                size_bytes=Path(self.backup_file_path).stat().st_size,
                checksum=MetadataChecksum(
                    algorithm=algorithm,
                    value=checksum,
                    verified=True,
                    last_verified=utcnow(),
                ),
            )
        )

    def restore_backup_in_database(self, db: Session, data: dict[str, Any]) -> None:
        for i, table in enumerate(Base.metadata.sorted_tables):
            print(f"{i}: {table}")

    def verify_backup_file(self) -> None:
        test_database_name = "restore_backup_test"
        temp_db_url = recreate_database(test_database_name)

        data = self._get_backup_file_data()

        try:
            with temporary_db_session(test_database_name) as db:
                self.restore_backup_in_database(db, data)

        finally:
            drop_database(temp_db_url)

    def _get_backup_file_data(self) -> dict[str, Any]:
        if self.backup_file_path is None:
            raise ValueError("Backup file path not set")

        if self.backup_file_path.suffix != ".json":
            raise ValueError("Backup file type not json")

        with self.backup_file_path.open("r") as file:
            data: dict[str, Any] = json.load(file)

        return data

    # ----------------------- File Backup ---------------------- #

    # ------------------------ Metadata ------------------------ #

    # -------------------------- Utils ------------------------- #

    def _write_to_json_file(self, file_path: Path, data: dict[str, Any]) -> None:
        with file_path.open("w") as file:
            json.dump(data, file, default=str)
