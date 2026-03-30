import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, cast


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


class TestAppConfig(AppConfig):
    # DATABASE
    DATABASE_USERNAME: str = "testing"
    DATABASE_PASSWORD: str = "testing"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5435
    DATABASE_DB_NAME: str = "testing"


APP_SETTINGS = AppConfig | TestAppConfig
ENVS = Literal["dev", "prod", "test"]


def get_app_config() -> APP_SETTINGS:
    environment: ENVS = cast(ENVS, os.getenv("APP_ENV", "dev"))

    match environment:
        case "dev":
            return AppConfig()  # type: ignore[call-arg]

        case "prod":
            raise NotImplementedError(
                "Settings for production have not yet been configured. May just be a duplicate of dev settings in the future."
            )

        case "test":
            return TestAppConfig()


app_config: APP_SETTINGS = get_app_config()
