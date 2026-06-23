from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SQLITE_PATH = Path(tempfile.gettempdir()) / "sentinelai.db"


class Settings(BaseSettings):
    app_name: str = "SentinelAI"
    app_env: str = "development"
    api_key: str = "sentinel-dev-key"
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
    vector_backend: str = "inmemory"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sentinelai_knowledge"
    use_langgraph: bool = False
    max_retrieval_results: int = Field(default=3, ge=1, le=10)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
