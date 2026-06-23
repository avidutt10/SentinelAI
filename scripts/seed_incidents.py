from __future__ import annotations

from sentinelai.core.db import create_db_and_tables, session_scope
from sentinelai.schemas.incident import IncidentCreate
from sentinelai.services.incident_service import IncidentService

INCIDENT_FIXTURES = [
    {
        "title": "API pods restarting with memory pressure",
        "severity": "high",
        "service": "api-service",
        "metadata": {"region": "us-east-1", "environment": "staging"},
        "logs": """2026-06-23T10:00:11Z service=api-service request volume spike detected
2026-06-23T10:01:22Z ERROR out of memory while handling checkout requests
2026-06-23T10:01:25Z kubelet killed process pid=1124 container=api-service
2026-06-23T10:02:05Z service=api-service pod restarted""",
    },
    {
        "title": "Checkout requests failing on database saturation",
        "severity": "high",
        "service": "checkout-service",
        "metadata": {"region": "us-west-2", "environment": "staging"},
        "logs": """2026-06-23T09:20:00Z service=checkout-service latency climbed above 4s
2026-06-23T09:21:10Z ERROR connection pool exhausted for postgres primary
2026-06-23T09:21:12Z WARN too many connections from app worker group
2026-06-23T09:22:00Z requests timed out waiting for db session""",
    },
]


def main() -> None:
    create_db_and_tables()
    with session_scope() as session:
        service = IncidentService(session)
        for item in INCIDENT_FIXTURES:
            service.create(IncidentCreate(**item))
    print(f"Seeded {len(INCIDENT_FIXTURES)} incidents.")


if __name__ == "__main__":
    main()
