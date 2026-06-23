from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from sentinelai.core.config import get_settings
from sentinelai.core.db import get_db


def require_api_key(x_api_key: str = Header(default="")) -> None:
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db
