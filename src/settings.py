import os
from pathlib import Path
from typing import Literal, cast

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # App Params
    APP_VERSION: str
    APP_ENV: str = "dev"

    # DATABASE
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_DB_NAME: str = "tracker"
    DATABASE_BACKUP_DB_NAME: str = "backup-tracker"

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_DB_NAME}"

    @property
    def backup_db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_BACKUP_DB_NAME}"

    # Celery
    REDIS_URL: str = "redis://redis:6379"

    @property
    def CELERY_URL(self):
        return f"{self.REDIS_URL}/0"

    # JWT tokens
    JWT_SECRET: str = ""
    JWT_EXPIRE_MINUTES: int = 480

    @model_validator(mode="after")
    def require_jwt_secret(self) -> Self:
        if self.JWT_SECRET == "":
            raise RuntimeError("JWT_SECRET must be set")

        return self

    # S3 Storage
    S3_HTTP_ADDRESS: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str

    # Maintenance
    TEMPORARY_PATH: str = "/temp"

    @model_validator(mode="after")
    def generate_temporary_path_folder(self) -> Self:
        temp_path = Path(self.TEMPORARY_PATH)
        temp_path.mkdir(parents=True, exist_ok=True)

        return self


class ProdAppConfig(AppConfig):
    model_config = SettingsConfigDict(
        env_file=".env.prod",
        extra="ignore",
    )

    APP_ENV: str = "prod"


class TestAppConfig(AppConfig):
    APP_VERSION: str = "0.0.1"
    APP_ENV: str = "test"

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/test_dbdt"

    @property
    def backup_db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/test_dbdt_backup"

    # JWT tokens
    JWT_SECRET: str = "test-token"

    # S3 Storage
    S3_HTTP_ADDRESS: str = "changed-in-fixture"
    S3_ACCESS_KEY: str = "test-access-key"
    S3_SECRET_KEY: str = "test-secret-key"
    S3_REGION: str = "us-east-1"

    # Maintenance
    TEMPORARY_PATH: str = "/test-temp"


APP_SETTINGS = AppConfig | TestAppConfig | ProdAppConfig
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

is_dev_env: bool = app_config.APP_ENV == "dev"
is_prod_env: bool = app_config.APP_ENV == "prod"
is_test_env: bool = app_config.APP_ENV == "test"
