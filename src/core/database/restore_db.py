import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

import src.models as table_objects
from src.models.base import Base, BaseModel
from src.models.task import TaskModel
from src.schemas.application_settings import ApplicationSettingsSchema
from src.settings import app_config


NO_BACKUP_TABLES = [TaskModel]
RESTRICTED_TABLES = [table.__tablename__ for table in NO_BACKUP_TABLES]


def application_is_configured_to_be_restored(
    configurable_settings: ApplicationSettingsSchema,
) -> bool:
    return configurable_settings.RESTORE_DATABASE_TO_BACKUP_ID is not None


def restore_logical_backup_in_database(
    database_name: str, backup_file_path: Path
) -> None:
    command = [
        "pg_restore",
        "--exit-on-error",
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
        backup_file_path,
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


def apply_ranged_backup_to_database(db: Session, data: dict[str, Any]) -> None:
    """
    NOTE: This requires that the database is already
    seeded with data from a logical backup before.
    """

    if type(db.bind) != Engine:
        raise ValueError("Database session has no engine attached")

    db_name = db.bind.engine.url.database  # ty: ignore[unresolved-attribute]

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
            for row in db.execute(select(model.c.id).where(model.c.id.in_(data_ids)))
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
