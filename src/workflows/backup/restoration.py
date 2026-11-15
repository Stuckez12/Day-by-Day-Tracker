import logging
from pathlib import Path
from typing import cast

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists

from src.core import LinkedList, LinkedNode
from src.core.database.db import temporary_db_session
from src.core.database.restore_db import restore_logical_backup_in_database
from src.settings import app_config
from src.utils import delete_folder, utcnow


class BackupRestorationWorkflow:
    def __init__(self) -> None:
        self.chain: LinkedList | None = None
        self.selected_chain_node: LinkedNode | None = None

    def use_chain(self, chain: LinkedList):
        self.chain = chain
        self.selected_chain_node = cast(LinkedNode, chain.get_next_node())

    def restore_new_database_to_logical_backup(self):
        restoration_db_name = app_config.DATABASE_DB_NAME
        self._create_restoration_database(app_config.db_url)

        restore_logical_backup_in_database(restoration_db_name, Path())

    def _create_restoration_database(self, restore_db: str) -> None:
        try:
            db_url = app_config.db_url + f"/{restore_db}"

            if database_exists(db_url):
                raise SystemError("Database already exists")

            create_database(db_url)

        except SQLAlchemyError:
            raise SystemError("Unable to create a new database")

    def rename_current_production_database(self):
        """
        Rename the current database to preserve it just in case we need to revert back to it
        """

        DEFAULT_DB_NAME = app_config.DATABASE_DB_NAME
        RESTORATION_BACKUP_DB_NAME = (
            DEFAULT_DB_NAME + f"_saved_before_restoration_at_{utcnow()}"
        )

        with temporary_db_session(app_config.DATABASE_MAINTENANCE_DB_NAME) as db:
            try:
                db.execute(
                    text(f"""
                    ALTER DATABASE {DEFAULT_DB_NAME} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                    ALTER DATABASE {DEFAULT_DB_NAME} MODIFY NAME = {RESTORATION_BACKUP_DB_NAME};
                    ALTER DATABASE {RESTORATION_BACKUP_DB_NAME} SET MULTI_USER;
                    """)
                )

            except SQLAlchemyError:
                logging.exception("Unable to rename the database")

                if database_exists(app_config.db_url):
                    try:
                        db.execute(
                            text(f"ALTER DATABASE {DEFAULT_DB_NAME} SET MULTI_USER;")
                        )

                    except SQLAlchemyError as err:
                        logging.error(f"""DEV Intervention Required!!!!!
When trying to recover the changes to the current database, an unexpected error occurred.
This occurred when trying to ALTER the potential SINGLE_USER state back into a MULTI_USER state.

Error Message:

{err}
""")

                raise SystemError("Unable to rename the database")

    def fully_restore_logical_database_to_latest_ranged_backup(self):
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
