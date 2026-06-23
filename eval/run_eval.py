from __future__ import annotations

import json
from pathlib import Path

from sentinelai.core.db import create_db_and_tables, session_scope
from sentinelai.schemas.incident import IncidentCreate
from sentinelai.schemas.knowledge import KnowledgeDocumentCreate
from sentinelai.services.incident_service import IncidentService
from sentinelai.services.investigation_service import InvestigationService
from sentinelai.services.knowledge_service import KnowledgeService
from scripts.seed_knowledge import KNOWLEDGE_FIXTURES

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def ensure_seeded() -> None:
    create_db_and_tables()
    with session_scope() as session:
        knowledge_service = KnowledgeService(session)
        for item in KNOWLEDGE_FIXTURES:
            knowledge_service.ingest(KnowledgeDocumentCreate(**item))


def main() -> None:
    ensure_seeded()
    results = []
    incident_paths = sorted(FIXTURE_DIR.glob("incident_[0-9][0-9][0-9].json"))
    with session_scope() as session:
        incident_service = IncidentService(session)
        investigation_service = InvestigationService(session)
        knowledge_service = KnowledgeService(session)
        for incident_path in incident_paths:
            expected_path = incident_path.with_name(f"{incident_path.stem}_expected.json")
            incident_payload = IncidentCreate(**json.loads(incident_path.read_text(encoding="utf-8")))
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            incident = incident_service.create(incident_payload)
            retrieval = knowledge_service.retrieve(
                query=f"{incident.title} {incident.service or ''} {incident.logs}",
                top_k=3,
            )
            report = investigation_service.investigate(incident.id)
            results.append(
                {
                    "fixture": incident_path.name,
                    "expected_root_cause_contains": expected["expected_root_cause_contains"],
                    "predicted_root_cause": report.root_cause,
                    "retrieved_doc_ids": [item.doc_id for item in retrieval],
                    "expected_doc_ids": expected["expected_doc_ids"],
                    "confidence": report.confidence,
                }
            )
    output_path = Path(__file__).resolve().parent / "results.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote eval results to {output_path}")


if __name__ == "__main__":
    main()
