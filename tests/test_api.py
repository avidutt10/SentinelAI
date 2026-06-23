from __future__ import annotations

from sentinelai.schemas.knowledge import KnowledgeDocumentCreate
from sentinelai.services.knowledge_service import KnowledgeService
from sentinelai.core.db import SessionLocal


def seed_knowledge() -> None:
    with SessionLocal() as session:
        service = KnowledgeService(session)
        service.ingest(
            KnowledgeDocumentCreate(
                doc_id="runbook_db_pool",
                title="Database connection pool exhaustion",
                doc_type="runbook",
                tags=["database", "pool"],
                content="Connection pool exhausted and too many connections errors usually indicate leaked sessions and slow queries.",
                metadata={},
            )
        )


def test_incident_crud(client, auth_headers) -> None:
    payload = {
        "title": "Checkout requests failing",
        "severity": "high",
        "service": "checkout-service",
        "metadata": {"environment": "test"},
        "logs": "2026-06-23T09:21:10Z ERROR connection pool exhausted for postgres primary",
    }
    response = client.post("/incidents", json=payload, headers=auth_headers)
    assert response.status_code == 201
    incident = response.json()
    assert incident["status"] == "submitted"

    get_response = client.get(f"/incidents/{incident['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == payload["title"]

    list_response = client.get("/incidents", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1


def test_knowledge_ingest_and_search(client, auth_headers) -> None:
    payload = {
        "doc_id": "runbook_timeout",
        "title": "Upstream timeout playbook",
        "doc_type": "runbook",
        "tags": ["timeout", "network"],
        "content": "Timeouts and connection resets often point to upstream health or TLS instability.",
        "metadata": {},
    }
    ingest = client.post("/knowledge/ingest", json=payload, headers=auth_headers)
    assert ingest.status_code == 201

    search = client.post("/knowledge/search", json={"query": "TLS timeout upstream", "top_k": 3}, headers=auth_headers)
    assert search.status_code == 200
    results = search.json()
    assert results
    assert results[0]["doc_id"] == "runbook_timeout"


def test_investigation_flow(client, auth_headers) -> None:
    seed_knowledge()
    incident_payload = {
        "title": "Checkout requests failing",
        "severity": "high",
        "service": "checkout-service",
        "metadata": {"environment": "test"},
        "logs": "\n".join(
            [
                "2026-06-23T09:20:00Z service=checkout-service latency climbed above 4s",
                "2026-06-23T09:21:10Z ERROR connection pool exhausted for postgres primary",
                "2026-06-23T09:21:12Z WARN too many connections from app worker group",
            ]
        ),
    }
    incident = client.post("/incidents", json=incident_payload, headers=auth_headers).json()
    investigate = client.post(f"/incidents/{incident['id']}/investigate", headers=auth_headers)
    assert investigate.status_code == 200

    report = client.get(f"/reports/incidents/{incident['id']}", headers=auth_headers)
    assert report.status_code == 200
    report_payload = report.json()
    assert "connection pool" in report_payload["root_cause"].lower()
    assert report_payload["remediation_steps"]

    traces = client.get(f"/reports/incidents/{incident['id']}/traces", headers=auth_headers)
    assert traces.status_code == 200
    assert len(traces.json()) == 3
