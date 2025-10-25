from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    async_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/org_directory"
    sync_url: str = "postgresql+psycopg://postgres:postgres@db:5432/org_directory"


class Settings(BaseSettings):
    """Конфигурация приложения."""

    app_name: str = "Organization Directory"
    api_prefix: str = "/api"
    api_v1_prefix: str = "/v1"
    api_key_header: str = "X-API-Key"
    api_key: str = "secret-key"

    database: DatabaseSettings = DatabaseSettings()
    log_sql: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        arbitrary_types_allowed=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

