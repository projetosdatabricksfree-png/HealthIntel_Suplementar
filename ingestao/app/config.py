from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="healthintel", alias="POSTGRES_DB")
    postgres_user: str = Field(default="healthintel", alias="POSTGRES_USER")
    postgres_password: str = Field(default="healthintel", alias="POSTGRES_PASSWORD")

    layout_service_host: str = Field(default="localhost", alias="LAYOUT_SERVICE_HOST")
    layout_service_port: int = Field(default=8001, alias="LAYOUT_SERVICE_PORT")
    layout_service_base_url: str | None = Field(default=None, alias="LAYOUT_SERVICE_BASE_URL")
    layout_service_token: str = Field(
        default="healthintel_layout_service_local_token_2026",
        alias="LAYOUT_SERVICE_TOKEN",
    )

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def layout_service_url(self) -> str:
        if self.layout_service_base_url:
            return self.layout_service_base_url.rstrip("/")
        return f"http://{self.layout_service_host}:{self.layout_service_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
