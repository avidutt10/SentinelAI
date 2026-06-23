from __future__ import annotations

from sentinelai.schemas.report import RootCauseReport


class ReviewerAgent:
    def run(self, report: RootCauseReport) -> RootCauseReport:
        confidence = report.confidence
        notes = report.reviewer_notes
        if len(report.supporting_evidence) < 2:
            confidence = max(0.3, confidence - 0.15)
            notes = "Limited supporting evidence was found. Human review is recommended."
        return RootCauseReport(
            root_cause=report.root_cause,
            confidence=round(confidence, 2),
            remediation_steps=report.remediation_steps,
            supporting_evidence=report.supporting_evidence,
            reviewer_notes=notes,
            escalation_required=report.escalation_required or confidence < 0.65,
        )
