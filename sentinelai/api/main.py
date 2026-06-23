from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from sentinelai.api.routes import incidents, knowledge, reports
from sentinelai.core.config import get_settings
from sentinelai.core.db import create_db_and_tables

structlog.configure()
settings = get_settings()
logger = structlog.get_logger(__name__)
static_index = Path(__file__).resolve().parents[2] / "static" / "index.html"

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    logger.info("startup_complete", app=settings.app_name, env=settings.app_env)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    return HTMLResponse(static_index.read_text(encoding="utf-8"))


app.include_router(incidents.router)
app.include_router(knowledge.router)
app.include_router(reports.router)
