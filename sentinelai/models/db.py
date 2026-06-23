from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    severity: Mapped[str] = mapped_column(String(50))
    service: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="submitted")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    logs: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    report: Mapped["InvestigationReport | None"] = relationship(back_populates="incident", uselist=False)
    traces: Mapped[list["AgentTrace"]] = relationship(back_populates="incident", cascade="all, delete-orphan")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(50))
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class InvestigationReport(Base):
    __tablename__ = "investigation_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), unique=True)
    root_cause: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    remediation_steps: Mapped[list[str]] = mapped_column(JSON, default=list)
    supporting_evidence: Mapped[list[dict]] = mapped_column(JSON, default=list)
    reviewer_notes: Mapped[str] = mapped_column(Text, default="")
    escalation_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    incident: Mapped[Incident] = relationship(back_populates="report")


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    agent_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="completed")
    summary: Mapped[str] = mapped_column(Text, default="")
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    incident: Mapped[Incident] = relationship(back_populates="traces")
