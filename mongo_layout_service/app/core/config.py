from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_LAYOUT_SERVICE_TOKEN = "healthintel_layout_service_local_token_2026"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"), env_file_encoding="utf-8", extra="ignore"
    )

    app_nome: str = "HealthIntel Layout Service"
    app_versao: str = "0.2.0"
    app_env: str = Field(default="local", alias="LAYOUT_SERVICE_ENV")
    app_host: str = Field(default="0.0.0.0", alias="LAYOUT_SERVICE_HOST")
    app_port: int = Field(default=8001, alias="LAYOUT_SERVICE_PORT")
    app_allowed_hosts: str = Field(
        default="localhost,127.0.0.1,testserver,mongo_layout_service,healthintel_layout_service",
        alias="LAYOUT_SERVICE_ALLOWED_HOSTS",
    )
    app_max_request_size_bytes: int = Field(
        default=1_048_576,
        alias="LAYOUT_SERVICE_MAX_REQUEST_SIZE_BYTES",
    )
    service_token: str = Field(default=DEFAULT_LAYOUT_SERVICE_TOKEN, alias="LAYOUT_SERVICE_TOKEN")
    mongo_host: str = Field(default="localhost", alias="MONGO_HOST")
    mongo_port: int = Field(default=27017, alias="MONGO_PORT")
    mongo_db: str = Field(default="healthintel_layout", alias="MONGO_DB")
    mongo_user: str = Field(default="healthintel", alias="MONGO_INITDB_ROOT_USERNAME")
    mongo_password: str = Field(default="healthintel", alias="MONGO_INITDB_ROOT_PASSWORD")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def mongo_dsn(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_password}"
            f"@{self.mongo_host}:{self.mongo_port}/?authSource=admin"
        )

    @property
    def trusted_hosts(self) -> list[str]:
        return [item.strip() for item in self.app_allowed_hosts.split(",") if item.strip()]

    def validar_configuracao(self) -> None:
        if self.app_env.lower() == "local":
            return
        if self.service_token == DEFAULT_LAYOUT_SERVICE_TOKEN:
            raise ValueError(
                "LAYOUT_SERVICE_TOKEN nao pode usar valor padrao fora do ambiente local."
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validar_configuracao()
    return settings
