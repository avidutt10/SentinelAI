from __future__ import annotations

import re

from sentinelai.schemas.agent import LogAnalysisResult, WorkflowState


class LogAnalysisAgent:
    anomaly_patterns = {
        "oom_kill": re.compile(r"(out of memory|oom|killed process)", re.IGNORECASE),
        "db_pool_exhaustion": re.compile(r"(connection pool exhausted|too many connections|max clients)", re.IGNORECASE),
        "deploy_regression": re.compile(r"(deployment completed|rollback|new release|version )", re.IGNORECASE),
        "network_timeout": re.compile(r"(timeout|connection reset|tls handshake)", re.IGNORECASE),
        "high_latency": re.compile(r"(latency|slow query|response time)", re.IGNORECASE),
    }

    def run(self, state: WorkflowState) -> LogAnalysisResult:
        logs = state.logs
        anomalies = [name for name, pattern in self.anomaly_patterns.items() if pattern.search(logs)]
        if not anomalies:
            anomalies = ["general_service_degradation"]
        timeline = self._timeline(logs)
        affected_services = list({service for service in [state.service, *self._services_from_logs(logs)] if service})
        summary = f"Incident '{state.title}' shows {', '.join(anomalies)} across {', '.join(affected_services or ['unknown services'])}."
        severity_hint = "high" if any(key in anomalies for key in ["oom_kill", "db_pool_exhaustion", "deploy_regression"]) else state.severity
        return LogAnalysisResult(
            summary=summary,
            anomalies=anomalies,
            timeline=timeline,
            affected_services=affected_services,
            severity_hint=severity_hint,
        )

    def _timeline(self, logs: str) -> list[str]:
        lines = [line.strip() for line in logs.splitlines() if line.strip()]
        if len(lines) <= 4:
            return lines
        return [lines[0], lines[len(lines) // 2], lines[-1]]

    def _services_from_logs(self, logs: str) -> list[str]:
        matches = re.findall(r"\b(service|component|pod)[:= ]([a-zA-Z0-9_-]+)", logs, re.IGNORECASE)
        return [match[1] for match in matches]
