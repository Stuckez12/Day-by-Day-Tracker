import logging
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.core.database.restore_db import restore_logical_backup_in_database
from src.settings import app_config
from src.utils import delete_folder


class BackupRestorationWorkflow:
    def __init__(self) -> None:
        pass

    def restore_new_database_to_backup(self):
        restoration_db_name = "restoration_db"
        self._create_restoration_database(restoration_db_name)

        restore_logical_backup_in_database(restoration_db_name, Path())

    def _create_restoration_database(self, restore_db: str) -> None:
        try:
            db_url = app_config.base_db_url + f"/{restore_db}"

            if database_exists(db_url):
                drop_database(db_url)

            create_database(db_url)

        except SQLAlchemyError:
            raise SystemError("Unable to create a new database")

    def rename_current_database(self):
        """
        Rename the current database to preserve it just in case we need to revert back to it
        """

        pass

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
