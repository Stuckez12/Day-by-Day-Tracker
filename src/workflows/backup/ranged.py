import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from sqlalchemy_utils import drop_database

import src.models as table_objects
from src.common.utils import utcnow
from src.core.database import temporary_db_session
from src.core.database.recreate_db import recreate_database
from src.core.s3_storage import ObjectStorage
from src.models import BackupModel, TaskModel
from src.models.base import Base, BaseModel
from src.schemas import DateRangeRequest
from src.schemas.backup import (
    MetadataChecksum,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.settings import app_config
from src.workflows.backup.base import BaseBackupWorkflow


NO_BACKUP_TABLES = [TaskModel]
RESTRICTED_TABLES = [table.__tablename__ for table in NO_BACKUP_TABLES]


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

        if type(db.bind) != Engine:
            raise ValueError("Database session has no engine attached")

        db_name = db.bind.engine.url.database

        if db_name is None:
            raise ValueError("Database name not found from session")

        all_tables: dict[str, type[BaseModel]] = {
            obj.__tablename__: obj
            for _, obj in vars(table_objects).items()
            # Only include imported objects you have defined
            if isinstance(obj, type)
            # Filter out all models that dont match Base
            and obj._sa_registry == Base.registry
            # Filter out models that are not backed up
            and obj.__tablename__ not in RESTRICTED_TABLES
        }

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option(
            "sqlalchemy.url", f"{app_config.base_db_url}/{db_name}"
        )
        command.upgrade(alembic_cfg, self.metadata.database_alembic_version)

        for model in Base.metadata.sorted_tables:
            model_obj = all_tables.get(model.name, None)
            table_data: list[dict[str, Any]] | None = data.get(model.name, None)

            if model_obj is None:
                continue

            if table_data is None:
                logging.warning(
                    f"Restoration of table '{model.name}' was not found in data"
                )
                continue

            logging.info(f"Ranged seeding table: '{model.name}'")

            data_ids = []
            id_mapping: dict[str, dict[str, Any]] = {}

            for row in table_data:
                data_id = row.get("id", None)

                if data_id is None:
                    continue

                data_ids.append(data_id)
                id_mapping[data_id] = row

            existing_ids = {
                str(row.id)
                for row in db.execute(
                    select(model.c.id).where(model.c.id.in_(data_ids))
                )
            }

            logging.debug(
                f"Existing {model.name} rows: {len(existing_ids)}/{len(table_data)}"
            )

            for data_id in existing_ids:
                db.execute(
                    model.update()
                    .where(model.c.id == data_id)
                    .values(**id_mapping[data_id])
                )

                id_mapping.pop(data_id)

            logging.debug(
                f"Remaining {model.name} rows to add: {len(id_mapping)}/{len(table_data)}"
            )

            for _, id_data in id_mapping.items():
                db.execute(model.insert().values(**id_data))

            db.flush()

        db.commit()

        logging.info("Seeded all ranged data")

    def verify_backup_file(self) -> None:
        """
        TODO LATER: explore this again later on and see whether this is still worth doing.
        This requires the ranged backup to be a part of a chain of backups.
        """
        test_database_name = "restore_backup_test"
        temp_db_url = recreate_database(test_database_name)

        data = self._get_backup_file_data()

        try:
            with temporary_db_session(test_database_name) as db:
                self.apply_ranged_backup_to_database(db, data)

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
