from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_LAYOUT_SERVICE_TOKEN = "healthintel_layout_service_local_token_2026"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_nome: str = "HealthIntel Suplementar API"
    app_versao: str = "0.1.0"
    app_prefixo: str = Field(default="/v1", alias="API_PREFIX")
    app_env: str = Field(default="local", alias="API_ENV")
    app_host: str = Field(default="0.0.0.0", alias="API_HOST")
    app_port: int = Field(default=8000, alias="API_PORT")
    app_rate_limit_rpm: int = Field(default=60, alias="API_RATE_LIMIT_RPM")
    app_rate_limit_fail_open: bool = Field(default=True, alias="API_RATE_LIMIT_FAIL_OPEN")
    app_cache_ttl_segundos: int = Field(default=60, alias="API_CACHE_TTL_SEGUNDOS")
    app_allowed_hosts: str = Field(
        default="localhost,127.0.0.1,testserver,api,healthintel_api",
        alias="API_ALLOWED_HOSTS",
    )
    app_cors_allowed_origins: str = Field(
        default="http://localhost:8080,http://127.0.0.1:8080",
        alias="API_CORS_ALLOWED_ORIGINS",
    )
    app_max_request_size_bytes: int = Field(default=1_048_576, alias="API_MAX_REQUEST_SIZE_BYTES")

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="healthintel", alias="POSTGRES_DB")
    postgres_user: str = Field(default="healthintel", alias="POSTGRES_USER")
    postgres_password: str = Field(default="healthintel", alias="POSTGRES_PASSWORD")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    mongo_host: str = Field(default="localhost", alias="MONGO_HOST")
    mongo_port: int = Field(default=27017, alias="MONGO_PORT")
    mongo_db: str = Field(default="healthintel_layout", alias="MONGO_DB")
    mongo_user: str = Field(default="healthintel", alias="MONGO_INITDB_ROOT_USERNAME")
    mongo_password: str = Field(default="healthintel", alias="MONGO_INITDB_ROOT_PASSWORD")
    layout_service_host: str = Field(default="localhost", alias="LAYOUT_SERVICE_HOST")
    layout_service_port: int = Field(default=8001, alias="LAYOUT_SERVICE_PORT")
    layout_service_base_url: str | None = Field(default=None, alias="LAYOUT_SERVICE_BASE_URL")
    layout_service_token: str = Field(
        default=DEFAULT_LAYOUT_SERVICE_TOKEN,
        alias="LAYOUT_SERVICE_TOKEN",
    )

    api_jwt_admin_secret: str = Field(default="trocar_em_producao", alias="API_JWT_ADMIN_SECRET")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def mongo_dsn(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_password}"
            f"@{self.mongo_host}:{self.mongo_port}/?authSource=admin"
        )

    @property
    def layout_service_url(self) -> str:
        if self.layout_service_base_url:
            return self.layout_service_base_url.rstrip("/")
        return f"http://{self.layout_service_host}:{self.layout_service_port}"

    @property
    def trusted_hosts(self) -> list[str]:
        return [item.strip() for item in self.app_allowed_hosts.split(",") if item.strip()]

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.app_cors_allowed_origins.split(",") if item.strip()]

    @property
    def rate_limit_falha_aberta(self) -> bool:
        ambientes_tolerantes = {"local", "dev", "test", "ci"}
        return self.app_rate_limit_fail_open and self.app_env.lower() in ambientes_tolerantes

    def validar_configuracao(self) -> None:
        if self.app_env.lower() == "local":
            return
        segredos_invalidos = []
        if self.api_jwt_admin_secret == "trocar_em_producao":
            segredos_invalidos.append("API_JWT_ADMIN_SECRET")
        if self.layout_service_token == DEFAULT_LAYOUT_SERVICE_TOKEN:
            segredos_invalidos.append("LAYOUT_SERVICE_TOKEN")
        if segredos_invalidos:
            raise ValueError(
                "Configuracao insegura para ambiente nao local: "
                + ", ".join(sorted(segredos_invalidos))
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validar_configuracao()
    return settings
