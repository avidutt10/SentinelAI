from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinelai.models.db import Incident
from sentinelai.schemas.incident import IncidentCreate


class IncidentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: IncidentCreate) -> Incident:
        incident = Incident(
            title=payload.title,
            severity=payload.severity,
            service=payload.service,
            metadata_json=payload.metadata,
            logs=payload.logs,
            status="submitted",
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get(self, incident_id: int) -> Incident:
        incident = self.db.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
        return incident

    def list(self, limit: int, offset: int) -> tuple[list[Incident], int]:
        items = self.db.scalars(select(Incident).order_by(Incident.created_at.desc()).limit(limit).offset(offset)).all()
        total = len(self.db.scalars(select(Incident.id)).all())
        return items, total

    def update_status(self, incident: Incident, status_value: str) -> Incident:
        incident.status = status_value
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident
