from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB_PATH = Path(tempfile.gettempdir()) / "sentinelai_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["VECTOR_BACKEND"] = "inmemory"
os.environ["USE_LANGGRAPH"] = "false"
os.environ["API_KEY"] = "test-key"

from sentinelai.api.main import app
from sentinelai.core.config import get_settings
from sentinelai.core.db import create_db_and_tables, engine
from sentinelai.models.db import Base


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    get_settings.cache_clear()
    Base.metadata.drop_all(bind=engine)
    create_db_and_tables()
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"x-api-key": "test-key"}
