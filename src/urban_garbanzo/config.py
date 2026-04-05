"""Settings and configuration management."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "urban-garbanzo"
    app_version: str = "0.1.0"
    debug: bool = False

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "sqlite://:memory:"

    log_level: str = "INFO"

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
