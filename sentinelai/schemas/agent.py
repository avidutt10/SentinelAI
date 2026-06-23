from __future__ import annotations

from pydantic import BaseModel, Field

from sentinelai.schemas.knowledge import KnowledgeSearchResult
from sentinelai.schemas.report import RootCauseReport


class LogAnalysisResult(BaseModel):
    summary: str
    anomalies: list[str]
    timeline: list[str]
    affected_services: list[str]
    severity_hint: str


class RetrievalAgentResult(BaseModel):
    query: str
    matches: list[KnowledgeSearchResult]


class WorkflowState(BaseModel):
    incident_id: int
    title: str
    severity: str
    service: str | None
    metadata: dict = Field(default_factory=dict)
    logs: str
    analysis: LogAnalysisResult | None = None
    retrieval: RetrievalAgentResult | None = None
    report: RootCauseReport | None = None
