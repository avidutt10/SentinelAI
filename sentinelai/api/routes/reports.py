from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sentinelai.api.dependencies import get_db_session, require_api_key
from sentinelai.schemas.report import AgentTraceRead, InvestigationReportRead
from sentinelai.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(require_api_key)])


@router.get("/incidents/{incident_id}", response_model=InvestigationReportRead)
def get_report_for_incident(incident_id: int, db: Session = Depends(get_db_session)) -> InvestigationReportRead:
    report = ReportService(db).get_report_for_incident(incident_id)
    return InvestigationReportRead(
        id=report.id,
        incident_id=report.incident_id,
        root_cause=report.root_cause,
        confidence=report.confidence,
        remediation_steps=report.remediation_steps,
        supporting_evidence=report.supporting_evidence,
        reviewer_notes=report.reviewer_notes,
        escalation_required=report.escalation_required,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get("/incidents/{incident_id}/traces", response_model=list[AgentTraceRead])
def get_traces_for_incident(incident_id: int, db: Session = Depends(get_db_session)) -> list[AgentTraceRead]:
    traces = ReportService(db).get_traces_for_incident(incident_id)
    return [
        AgentTraceRead(
            id=trace.id,
            incident_id=trace.incident_id,
            agent_name=trace.agent_name,
            status=trace.status,
            summary=trace.summary,
            input_payload=trace.input_payload,
            output_payload=trace.output_payload,
            confidence=trace.confidence,
            latency_ms=trace.latency_ms,
            created_at=trace.created_at,
        )
        for trace in traces
    ]
