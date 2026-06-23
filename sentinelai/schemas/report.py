from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class InvestigationReportRead(BaseModel):
    id: int
    incident_id: int
    root_cause: str
    confidence: float
    remediation_steps: list[str]
    supporting_evidence: list[dict]
    reviewer_notes: str
    escalation_required: bool
    created_at: datetime
    updated_at: datetime


class AgentTraceRead(BaseModel):
    id: int
    incident_id: int
    agent_name: str
    status: str
    summary: str
    input_payload: dict
    output_payload: dict
    confidence: float | None
    latency_ms: int
    created_at: datetime


class RootCauseReport(BaseModel):
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    remediation_steps: list[str]
    supporting_evidence: list[dict]
    reviewer_notes: str
    escalation_required: bool
