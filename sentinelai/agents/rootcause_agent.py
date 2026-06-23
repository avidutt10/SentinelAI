from __future__ import annotations

from sentinelai.schemas.agent import WorkflowState
from sentinelai.schemas.report import RootCauseReport


class RootCauseFixAgent:
    cause_map = {
        "oom_kill": (
            "Service likely exhausted available memory and was terminated by the runtime.",
            [
                "Scale the affected service horizontally or increase memory limits.",
                "Inspect recent memory growth and heap usage to isolate the leak or spike.",
                "Add alerts on memory saturation before OOM termination occurs.",
            ],
        ),
        "db_pool_exhaustion": (
            "Application requests likely exhausted the database connection pool.",
            [
                "Inspect pool sizing and long-running queries.",
                "Reduce connection leaks and increase pool limits if justified.",
                "Add query latency dashboards and connection pool alerts.",
            ],
        ),
        "deploy_regression": (
            "A recent deployment likely introduced a regression affecting service stability.",
            [
                "Compare the failing version against the last healthy release.",
                "Rollback or disable the suspect change behind a feature flag.",
                "Add deploy annotations to incident dashboards for faster correlation.",
            ],
        ),
        "network_timeout": (
            "The incident appears driven by an upstream connectivity or network timeout issue.",
            [
                "Validate upstream health and retry behavior.",
                "Inspect DNS, TLS, and network path errors around the failure window.",
                "Tune timeouts and circuit-breaking for the dependent call path.",
            ],
        ),
        "high_latency": (
            "The system is experiencing latency degradation, likely from a stressed dependency.",
            [
                "Check saturation on the slowest dependency or resource path.",
                "Profile high-latency requests and cache opportunities.",
                "Add SLO alerts tied to p95 and p99 latency.",
            ],
        ),
        "general_service_degradation": (
            "The available evidence suggests general service degradation, but the exact cause remains uncertain.",
            [
                "Gather more granular logs and metrics from the failure window.",
                "Correlate the incident with recent infra and deploy events.",
                "Escalate to an operator if the issue persists without clearer evidence.",
            ],
        ),
    }

    def run(self, state: WorkflowState) -> RootCauseReport:
        assert state.analysis is not None
        assert state.retrieval is not None
        primary_anomaly = state.analysis.anomalies[0]
        root_cause, remediation_steps = self.cause_map.get(primary_anomaly, self.cause_map["general_service_degradation"])
        supporting_evidence = [
            {"type": "analysis", "value": state.analysis.summary},
            *[
                {"type": "knowledge", "doc_id": match.doc_id, "title": match.title, "score": match.score}
                for match in state.retrieval.matches
            ],
        ]
        confidence = 0.55 + min(0.35, 0.1 * len(state.retrieval.matches))
        if primary_anomaly == "general_service_degradation":
            confidence = 0.45
        reviewer_notes = "Evidence is sufficient for a first-pass recommendation." if confidence >= 0.7 else "Confidence is moderate; a human should confirm before acting."
        escalation_required = confidence < 0.65
        return RootCauseReport(
            root_cause=root_cause,
            confidence=round(confidence, 2),
            remediation_steps=remediation_steps,
            supporting_evidence=supporting_evidence,
            reviewer_notes=reviewer_notes,
            escalation_required=escalation_required,
        )
