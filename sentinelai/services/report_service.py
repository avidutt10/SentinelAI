from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinelai.models.db import AgentTrace, InvestigationReport


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_report_for_incident(self, incident_id: int) -> InvestigationReport:
        report = self.db.scalar(select(InvestigationReport).where(InvestigationReport.incident_id == incident_id))
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        return report

    def get_traces_for_incident(self, incident_id: int) -> list[AgentTrace]:
        return self.db.scalars(
            select(AgentTrace).where(AgentTrace.incident_id == incident_id).order_by(AgentTrace.created_at.asc())
        ).all()
