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

    # PGADMIN
    PGADMIN_EMAIL: str
    PGADMIN_PASSWORD: str

    # API
    API_HOST: str
    API_PORT: int

    # FRONTEND
    FRONTEND_HOST: str
    FRONTEND_HOST_NAME: str | None
    FRONTEND_PORT: int

    @property
    def frontend_url(self):
        if self.FRONTEND_HOST_NAME is not None:
            return f"http://{self.FRONTEND_HOST_NAME}:{self.FRONTEND_PORT}"

        return f"http://{self.FRONTEND_HOST}:{self.FRONTEND_PORT}"

    # API KEYS
    TAILSCALE_API_KEY: str


class TestAppConfig(AppConfig):
    model_config = SettingsConfigDict(
        env_file=".env.testing",
        extra="ignore",
    )

    # DATABASE
    DATABASE_USERNAME: str = "testing"
    DATABASE_PASSWORD: str = "testing"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5435
    DATABASE_DB_NAME: str = "testing"

    # PGADMIN
    PGADMIN_EMAIL: None = None  # type: ignore[assignment]
    PGADMIN_PASSWORD: None = None  # type: ignore[assignment]

    # API
    API_HOST: None = None  # type: ignore[assignment]
    API_PORT: None = None  # type: ignore[assignment]

    # FRONTEND
    FRONTEND_HOST: None = None  # type: ignore[assignment]
    FRONTEND_HOST_NAME: None = None  # type: ignore[assignment]
    FRONTEND_PORT: None = None  # type: ignore[assignment]

    # API KEYS
    TAILSCALE_API_KEY: None = None  # type: ignore[assignment]


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
