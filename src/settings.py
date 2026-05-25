import os
from typing import Literal, cast

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # DATABASE
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_DB_NAME: str

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_DB_NAME}"

    # Celery
    REDIS_URL: str = "redis://redis:6379"

    @property
    def CELERY_URL(self):
        return f"{self.REDIS_URL}/0"

    # Maintenance
    BACKUP_PATH: str


class ProdAppConfig(AppConfig):
    model_config = SettingsConfigDict(
        env_file=".env.prod",
        extra="ignore",
    )


class TestAppConfig(AppConfig):
    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/test_dbdt"

    # Maintenance
    BACKUP_PATH: str = "/"


APP_SETTINGS = AppConfig | TestAppConfig
ENVS = Literal["dev", "prod", "test"]


def get_app_config() -> APP_SETTINGS:
    environment: ENVS = cast(ENVS, os.getenv("APP_ENV", "dev"))

    match environment:
        case "dev":
            return AppConfig()  # type: ignore < auto gets from env

        case "prod":
            return ProdAppConfig()  # type: ignore < auto gets from env

        case "test":
            return TestAppConfig()  # type: ignore < auto gets from env


app_config: APP_SETTINGS = get_app_config()

is_dev_env: bool = isinstance(app_config, AppConfig)
is_prod_env: bool = isinstance(app_config, ProdAppConfig)
is_test_env: bool = isinstance(app_config, TestAppConfig)
