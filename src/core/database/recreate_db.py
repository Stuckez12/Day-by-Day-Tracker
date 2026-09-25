from sqlalchemy_utils import create_database, database_exists, drop_database

from src.settings import app_config


def recreate_database(db_name: str):
    db_url = f"postgresql+psycopg2://{app_config.DATABASE_USERNAME}:{app_config.DATABASE_PASSWORD}@{app_config.DATABASE_HOST}:{app_config.DATABASE_PORT}/{db_name}"

    if database_exists(db_url):
        drop_database(db_url)

    create_database(db_url)

    return db_url
