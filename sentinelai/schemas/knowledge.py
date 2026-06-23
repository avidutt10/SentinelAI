from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    doc_id: str = Field(min_length=3, max_length=100)
    title: str = Field(min_length=3, max_length=200)
    doc_type: str = Field(pattern="^(runbook|postmortem)$")
    tags: list[str] = Field(default_factory=list)
    content: str = Field(min_length=20)
    source: str | None = None
    metadata: dict = Field(default_factory=dict)


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=10)


class KnowledgeSearchResult(BaseModel):
    doc_id: str
    title: str
    doc_type: str
    score: float
    tags: list[str]
    excerpt: str


class KnowledgeDocumentRead(BaseModel):
    id: int
    doc_id: str
    title: str
    doc_type: str
    tags: list[str]
    content: str
    source: str | None
    metadata: dict
    created_at: datetime
