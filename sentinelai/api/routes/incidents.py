from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from sentinelai.api.dependencies import get_db_session, require_api_key
from sentinelai.schemas.incident import IncidentCreate, IncidentList, IncidentRead, InvestigationTriggerResponse
from sentinelai.schemas.report import AgentTraceRead, InvestigationReportRead
from sentinelai.services.incident_service import IncidentService
from sentinelai.services.investigation_service import InvestigationService
from sentinelai.services.report_service import ReportService

router = APIRouter(prefix="/incidents", tags=["incidents"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db_session)) -> IncidentRead:
    incident = IncidentService(db).create(payload)
    return IncidentRead(
        id=incident.id,
        title=incident.title,
        severity=incident.severity,
        service=incident.service,
        status=incident.status,
        metadata=incident.metadata_json,
        logs=incident.logs,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )


@router.get("", response_model=IncidentList)
def list_incidents(
    db: Session = Depends(get_db_session),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> IncidentList:
    items, total = IncidentService(db).list(limit=limit, offset=offset)
    return IncidentList(
        items=[
            IncidentRead(
                id=item.id,
                title=item.title,
                severity=item.severity,
                service=item.service,
                status=item.status,
                metadata=item.metadata_json,
                logs=item.logs,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ],
        total=total,
    )


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db_session)) -> IncidentRead:
    incident = IncidentService(db).get(incident_id)
    return IncidentRead(
        id=incident.id,
        title=incident.title,
        severity=incident.severity,
        service=incident.service,
        status=incident.status,
        metadata=incident.metadata_json,
        logs=incident.logs,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )


@router.post("/{incident_id}/investigate", response_model=InvestigationTriggerResponse)
def investigate_incident(incident_id: int, db: Session = Depends(get_db_session)) -> InvestigationTriggerResponse:
    report = InvestigationService(db).investigate(incident_id)
    return InvestigationTriggerResponse(incident_id=incident_id, status="completed", report_id=report.id)


@router.get("/{incident_id}/report", response_model=InvestigationReportRead)
def get_incident_report(incident_id: int, db: Session = Depends(get_db_session)) -> InvestigationReportRead:
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


@router.get("/{incident_id}/traces", response_model=list[AgentTraceRead])
def get_incident_traces(incident_id: int, db: Session = Depends(get_db_session)) -> list[AgentTraceRead]:
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
