import json
import logging
from pathlib import Path
from typing import cast
from zipfile import ZipFile

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists

from src.core import LinkedList, LinkedNode
from src.core.database.db import temporary_db_session
from src.core.database.restore_db import (
    apply_ranged_backup_to_database,
    restore_logical_backup_in_database,
)
from src.enums import BackupType
from src.models.base import Base
from src.schemas import BackupLink
from src.settings import app_config
from src.utils import delete_folder, utcnow


class BackupRestorationWorkflow:
    def __init__(self) -> None:
        self.chain: LinkedList | None = None
        self.selected_chain_node: LinkedNode | None = None

    def use_chain(self, chain: LinkedList):
        self.chain = chain
        self.selected_chain_node = cast(LinkedNode, chain.get_next_node())

    def restore_new_database_to_logical_backup(self) -> None:
        if self.selected_chain_node is None:
            raise ValueError("No backup chain node selected")

        backup: BackupLink = self.selected_chain_node.item

        logging.info(self.chain)

        if backup.backup_type != BackupType.LOGICAL:
            raise ValueError("Selected backup must be of type LOGICAL")

        with ZipFile(backup.zip_file_path, "r") as archive:
            dump_file = next(
                name for name in archive.namelist() if name.endswith(".dump")
            )
            backup_file_path = Path(
                archive.extract(dump_file, backup.zip_file_path.parent)
            )

        self._create_restoration_database(app_config.DATABASE_RESTORATION_DB_NAME)
        restore_logical_backup_in_database(
            app_config.DATABASE_RESTORATION_DB_NAME, backup_file_path
        )

    def _create_restoration_database(self, restore_db: str) -> None:
        try:
            db_url = f"{app_config.base_db_url}/{restore_db}"

            if database_exists(db_url):
                raise SystemError("Database already exists")

            create_database(db_url)

        except SQLAlchemyError:
            raise SystemError("Unable to create a new database")

    def validate_restored_database(self) -> None:
        with temporary_db_session(app_config.DATABASE_RESTORATION_DB_NAME) as db:
            for table in Base.metadata.sorted_tables:
                db.execute(select(table).limit(0))

    def switch_restored_database_into_service(self) -> str:
        db_name = app_config.DATABASE_DB_NAME
        numeric_date = int(utcnow().timestamp())

        saved_name = f"{db_name}_saved_{numeric_date}"

        with temporary_db_session(app_config.DATABASE_MAINTENANCE_DB_NAME) as db:
            production = db_name.replace('"', '""')
            saved = saved_name.replace('"', '""')
            restored = app_config.DATABASE_RESTORATION_DB_NAME.replace('"', '""')

            db.execute(
                text(f"""
                    ALTER DATABASE "{production}" ALLOW_CONNECTIONS false;
                    ALTER DATABASE "{restored}" ALLOW_CONNECTIONS false;
                    SELECT pg_terminate_backend(pid, 5000)
                    FROM pg_stat_activity WHERE datname IN (:production, :restored);
                    ALTER DATABASE "{production}" RENAME TO "{saved}";
                    ALTER DATABASE "{restored}" RENAME TO "{production}";
                    ALTER DATABASE "{production}" ALLOW_CONNECTIONS true;
                """),
                {
                    "production": db_name,
                    "restored": app_config.DATABASE_RESTORATION_DB_NAME,
                },
            )
            db.commit()

        return saved_name

    def fully_restore_logical_database_to_latest_ranged_backup(self):
        if self.chain is None or self.selected_chain_node is None:
            raise ValueError("No backup chain node selected")

        node = self.chain.get_next_node(self.selected_chain_node)

        with temporary_db_session(app_config.DATABASE_RESTORATION_DB_NAME) as db:
            while node is not None:
                backup: BackupLink = node.item

                if backup.backup_type not in (
                    BackupType.RANGED_DAY,
                    BackupType.RANGED_WEEK,
                ):
                    raise SystemError(
                        "Backup chain has a second logical backup within the chain"
                    )

                with ZipFile(backup.zip_file_path, "r") as archive:
                    with archive.open("dump.json") as file:
                        data = json.load(file)

                apply_ranged_backup_to_database(db, data)

                self.selected_chain_node = node
                node = self.chain.get_next_node(node)

    def cleanup_folder(self, folder: Path) -> None:
        try:
            delete_folder(folder)

        except FileNotFoundError:
            # What we expect to happen
            pass

        except FileExistsError:
            logging.error("Failed to clean up backup restoration workflow temp files")

        except Exception:
            logging.error(
                "Unknown error whilst trying to clean up BackupRestorationWorkflow temp folder"
            )
