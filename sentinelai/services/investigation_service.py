from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from sentinelai.agents.workflow import InvestigationWorkflow
from sentinelai.models.db import AgentTrace, Incident, InvestigationReport
from sentinelai.schemas.agent import WorkflowState
from sentinelai.services.incident_service import IncidentService


class InvestigationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_service = IncidentService(db)

    def investigate(self, incident_id: int) -> InvestigationReport:
        incident = self.incident_service.get(incident_id)
        self.incident_service.update_status(incident, "investigating")
        state = WorkflowState(
            incident_id=incident.id,
            title=incident.title,
            severity=incident.severity,
            service=incident.service,
            metadata=incident.metadata_json,
            logs=incident.logs,
        )
        final_state, traces = InvestigationWorkflow(self.db).run(state)
        report = self._save_report(incident, final_state.report)
        self._replace_traces(incident.id, traces)
        self.incident_service.update_status(incident, "investigated")
        return report

    def _save_report(self, incident: Incident, report_data) -> InvestigationReport:
        existing = self.db.scalar(select(InvestigationReport).where(InvestigationReport.incident_id == incident.id))
        if existing:
            existing.root_cause = report_data.root_cause
            existing.confidence = report_data.confidence
            existing.remediation_steps = report_data.remediation_steps
            existing.supporting_evidence = report_data.supporting_evidence
            existing.reviewer_notes = report_data.reviewer_notes
            existing.escalation_required = report_data.escalation_required
            report = existing
        else:
            report = InvestigationReport(
                incident_id=incident.id,
                root_cause=report_data.root_cause,
                confidence=report_data.confidence,
                remediation_steps=report_data.remediation_steps,
                supporting_evidence=report_data.supporting_evidence,
                reviewer_notes=report_data.reviewer_notes,
                escalation_required=report_data.escalation_required,
            )
            self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def _replace_traces(self, incident_id: int, traces: list[AgentTrace]) -> None:
        self.db.execute(delete(AgentTrace).where(AgentTrace.incident_id == incident_id))
        for trace in traces:
            self.db.add(trace)
        self.db.commit()
