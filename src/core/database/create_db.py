from sqlalchemy_utils import create_database, database_exists

from src.settings import app_config


def create_db():
    if not database_exists(app_config.backup_db_url):
        create_database(app_config.backup_db_url)

    if not database_exists(app_config.db_url):
        create_database(app_config.db_url)
