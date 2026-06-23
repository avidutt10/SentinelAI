from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    severity: str = Field(default="medium")
    service: str | None = None
    metadata: dict = Field(default_factory=dict)
    logs: str = Field(min_length=10)


class IncidentRead(BaseModel):
    id: int
    title: str
    severity: str
    service: str | None
    status: str
    metadata: dict
    logs: str
    created_at: datetime
    updated_at: datetime


class IncidentList(BaseModel):
    items: list[IncidentRead]
    total: int


class InvestigationTriggerResponse(BaseModel):
    incident_id: int
    status: str
    report_id: int
