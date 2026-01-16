from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_DB_NAME: str

    PGADMIN_EMAIL: str
    PGADMIN_PASSWORD: str

    API_HOST: str
    API_PORT: int

    FRONTEND_HOST: str
    FRONTEND_PORT: int

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_DB_NAME}"

    @property
    def frontend_url(self):
        return f"http://{self.FRONTEND_HOST}:{self.FRONTEND_PORT}"


class ApiKeyConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    TAILSCALE_API_KEY: str


app_config = AppConfig()
api_key_config = ApiKeyConfig()
