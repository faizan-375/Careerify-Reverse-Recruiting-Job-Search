from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Resolve the key file relative to this backend package, not the shell's
    # current directory (which may be the repository root when Uvicorn starts).
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    serpapi_api_key: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
