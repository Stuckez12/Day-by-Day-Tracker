import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.core.database.restore_db import (
    RESTRICTED_TABLES,
    apply_ranged_backup_to_database,
)
from src.core.s3_storage import ObjectStorage
from src.enums import BackupStatus
from src.models import BackupModel, MetaModel
from src.models.base import Base
from src.schemas import (
    DateRangeRequest,
    MetadataChecksum,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.services import TaskService
from src.utils import utcnow
from src.workflows.backup.base import BaseBackupWorkflow


class RangedBackupWorkflow(BaseBackupWorkflow):
    def __init__(
        self,
        *,
        db: Session,
        backup_db: Session,
        backup_record: BackupModel,
        object_storage: ObjectStorage,
        task_service: TaskService,
        date_range: DateRangeRequest,
    ) -> None:
        super().__init__(
            db=db,
            backup_db=backup_db,
            backup_record=backup_record,
            object_storage=object_storage,
            task_service=task_service,
        )

        self.start_date = date_range.min_date
        self.end_date = date_range.max_date

        self.metadata_date_range = MetadataDateRange(
            start=datetime.combine(date_range.min_date, datetime.min.time()),
            end=datetime.combine(date_range.max_date, datetime.min.time()),
        )

    # ------------------------ DB Backup ----------------------- #

    def create_ranged_backup(self) -> None:
        self._was_workflow_cancelled()

        result = {}
        self.metadata_date_range = cast(MetadataDateRange, self.metadata_date_range)

        for table in Base.metadata.sorted_tables:
            if table.fullname in RESTRICTED_TABLES:
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

    def apply_ranged_backup_to_database(
        self, db: Session, data: dict[str, Any]
    ) -> None:
        """
        NOTE: This requires that the database is already
        seeded with data from a logical backup before.
        """

        if self.metadata is None:
            raise ValueError("Metadata not set")

        apply_ranged_backup_to_database(db, data)

    def verify_backup_file(self) -> None:
        """
        TODO LATER: explore this again later on and see whether this is still worth doing.
        This requires the ranged backup to be a part of a chain of backups.
        """

        raise NotImplementedError("To be completed")

        # test_database_name = "restore_backup_test"
        # temp_db_url = recreate_database(test_database_name)

        # data = self._get_backup_file_data()

        # try:
        #     alembic_cfg = Config("alembic.ini")
        #     alembic_cfg.set_main_option(
        #         "sqlalchemy.url", f"{app_config.base_db_url}/{db_name}"
        #     )
        #     command.upgrade(alembic_cfg, self.metadata.database_alembic_version)

        #     with temporary_db_session(test_database_name) as db:
        #         self.apply_ranged_backup_to_database(db, data)

        # finally:
        #     drop_database(temp_db_url)

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

    def link_parent_backup(self):
        """This can be either a LOGICAL or RANGED backup. UPLOADED is also allowed as they are LOGICAL in disguise"""

        if self.backup_record.meta is None:
            raise ValueError("Backup record does not have any attached metadata")

        assert self.metadata_date_range, (
            "Somehow the RangedBackupWorkflow was incorrectly initialised"
        )

        backup = (
            self.backup_db.query(BackupModel)
            .join(MetaModel, BackupModel.id == MetaModel.backup_id)
            .filter(
                BackupModel.id != self.backup_record.id,
                BackupModel.status == BackupStatus.SUCCESS,
                MetaModel.date_range_end < self.metadata_date_range.start,
            )
            .order_by(desc(MetaModel.date_range_end))
            .first()
        )

        if backup is not None:
            logging.info(f"Linking ranged backup to existing backup: {backup.id}")
            self.backup_record.parent_backup_id = backup.id
