import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from celery.exceptions import OperationalError
from celery.result import AsyncResult
from sqlalchemy import Engine, MetaData, select
from sqlalchemy.orm import Session

from src.core.database import temporary_db_session
from src.enums.task_status import TaskStatus
from src.models import TaskModel
from src.schemas import TaskPaginated
from src.schemas.application_settings import ApplicationSettingsSchema
from src.services import TaskService
from src.settings import app_config
from src.utils import utcnow


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

    metadata = MetaData()
    metadata.reflect(bind=db.connection())
    unknown_tables = set(data) - set(metadata.tables) - set(RESTRICTED_TABLES)

    if unknown_tables:
        raise ValueError(f"Unknown tables in ranged backup: {sorted(unknown_tables)}")

    for model in metadata.sorted_tables:
        if model.name in RESTRICTED_TABLES or model.name == "alembic_version":
            continue

        table_data: list[dict[str, Any]] | None = data.get(model.name, None)

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
            date_time = utcnow()
            db.execute(
                model.update()
                .where(model.c.id == data_id)
                .values(
                    **id_mapping[data_id], created_at=date_time, updated_at=date_time
                )
            )

            id_mapping.pop(data_id)

        logging.debug(
            f"Remaining {model.name} rows to add: {len(id_mapping)}/{len(table_data)}"
        )

        for _, id_data in id_mapping.items():
            date_time = utcnow()
            db.execute(
                model.insert().values(
                    **id_data, created_at=date_time, updated_at=date_time
                )
            )

        db.flush()

    db.commit()

    logging.info("Seeded all ranged data")


def _check_if_restoration_workflow_is_running(
    configurable_settings: ApplicationSettingsSchema,
) -> bool:
    with temporary_db_session(app_config.DATABASE_DB_NAME) as db:
        task_service = TaskService(db)
        filter = TaskPaginated(
            name="database_restoration",
            task_status=[TaskStatus.PENDING, TaskStatus.RUNNING],
        )
        query = task_service.get_paginated_query(filter)

        restoration_tasks = query.all()

        if not restoration_tasks:
            return True

        if not configurable_settings.CANCEL_CURRENT_RESTORE_DATABASE_TASK:
            return False

        from src.main import celery_app

        for task in restoration_tasks:
            try:
                logging.debug(f"Revoking restoration celery task '{task.task_id}'")
                celery_app.control.revoke(str(task.task_id), terminate=True)

            except OperationalError as exc:
                error_msg = f"Unable to cancel restoration celery task '{task.task_id}'"
                logging.exception(error_msg)

                raise SystemError(error_msg) from exc

            task_service.cancel_task(task)

    return True


def run_restoration_task(
    configurable_settings: ApplicationSettingsSchema,
) -> AsyncResult:
    can_run_restoration: bool = _check_if_restoration_workflow_is_running(
        configurable_settings
    )

    if can_run_restoration:
        from src.tasks import database_restoration

        return database_restoration.delay()

    raise SystemError("There is a celery task running the restoration workflow")
