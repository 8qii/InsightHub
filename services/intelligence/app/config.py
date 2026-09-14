from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

ENV_FILES = tuple(parent / ".env" for parent in Path(__file__).resolve().parents)


class Settings(BaseSettings):
    """Runtime configuration loaded from the environment and optional .env file."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "InsightHub Intelligence Service"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    intelligence_port: PositiveInt = 8000

    anythingllm_base_url: str | None = None
    anythingllm_api_key: str | None = None
    anythingllm_timeout_seconds: float = Field(default=30.0, gt=0, le=300)

    llm_provider: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None
    embedding_provider: str | None = None
    embedding_model: str | None = None

    postgres_host: str | None = None
    postgres_port: PositiveInt = 5432
    postgres_database: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None

    @property
    def postgres_configured(self) -> bool:
        return all(
            value is not None and value != ""
            for value in (
                self.postgres_host,
                self.postgres_database,
                self.postgres_user,
                self.postgres_password,
            )
        )

    @property
    def postgres_url(self) -> URL:
        if not self.postgres_configured:
            raise ValueError("PostgreSQL configuration is incomplete")
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_database,
        )

    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str | None = None
    langfuse_enabled: bool = False

    data_dir: Path = Field(default=Path("./data"))
    max_upload_size_mb: PositiveInt = 100
    duckdb_path: Path = Field(default=Path("/data/analytics.duckdb"))
    evaluation_dataset_path: Path = Field(default=Path("evaluation/datasets"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
