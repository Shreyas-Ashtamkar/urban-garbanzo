"""Settings and configuration management."""

from typing import Literal
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from urban_garbanzo import __version__


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "urban-garbanzo"
    app_version: str = __version__
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite://:memory:"
    database_generate_schemas: bool = False
    log_level: str = "INFO"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    llm_provider: Literal["none", "openai", "anthropic"] = "none"
    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-3-5-haiku-latest"
    openai_base_url: str | None = None
    heuristic_weight: float = 0.3
    llm_weight: float = 0.7

    @property
    def tortoise_database_url(self) -> str:
        """Normalize database URLs into a scheme Tortoise understands."""

        if self.database_url.startswith("postgresql://"):
            parts = urlsplit(self.database_url)
            return urlunsplit(("postgres", parts.netloc, parts.path, parts.query, parts.fragment))
        return self.database_url


settings = Settings()
