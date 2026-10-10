from sqlalchemy_utils import create_database, database_exists, drop_database

from src.settings import app_config


def recreate_database(db_name: str):
    db_url = f"{app_config.base_db_url}/{db_name}"

    if database_exists(db_url):
        drop_database(db_url)

    create_database(db_url)

    return db_url
