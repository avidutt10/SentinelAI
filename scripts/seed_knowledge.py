from __future__ import annotations

from sentinelai.core.db import create_db_and_tables, session_scope
from sentinelai.schemas.knowledge import KnowledgeDocumentCreate
from sentinelai.services.knowledge_service import KnowledgeService

KNOWLEDGE_FIXTURES = [
    {
        "doc_id": "runbook_oom_api",
        "title": "OOM kills in API service",
        "doc_type": "runbook",
        "tags": ["memory", "oom", "api"],
        "content": "When api-service pods show out of memory errors or killed process messages, inspect heap growth, request spikes, and memory limits. Restarting helps briefly but does not fix the root cause.",
        "source": "internal/runbooks/oom-api",
        "metadata": {"category": "memory"},
    },
    {
        "doc_id": "runbook_db_pool",
        "title": "Database connection pool exhaustion",
        "doc_type": "runbook",
        "tags": ["database", "pool", "postgres"],
        "content": "Connection pool exhausted and too many connections errors usually indicate leaked sessions, slow queries, or pool sizing mismatches. Investigate active connections and application transaction handling.",
        "source": "internal/runbooks/db-pool",
        "metadata": {"category": "database"},
    },
    {
        "doc_id": "runbook_network_timeout",
        "title": "Upstream timeout troubleshooting",
        "doc_type": "runbook",
        "tags": ["network", "timeout", "upstream"],
        "content": "Timeouts and connection resets should be correlated with upstream health, DNS changes, TLS issues, and retry storms. Confirm if failures are isolated to one dependency path.",
        "source": "internal/runbooks/network-timeouts",
        "metadata": {"category": "network"},
    },
    {
        "doc_id": "runbook_latency",
        "title": "High latency response playbook",
        "doc_type": "runbook",
        "tags": ["latency", "performance", "slo"],
        "content": "If response time spikes or slow query warnings appear, inspect p95 latency by dependency, cache churn, and queue depth. Focus first on the narrowest stressed resource.",
        "source": "internal/runbooks/high-latency",
        "metadata": {"category": "performance"},
    },
    {
        "doc_id": "runbook_deploy_regression",
        "title": "New deployment regression triage",
        "doc_type": "runbook",
        "tags": ["deploy", "rollback", "release"],
        "content": "When incidents begin immediately after deployment completed events, compare release diffs, disable new flags, and consider rollback if error rates or latency regressions are clear.",
        "source": "internal/runbooks/deploy-regression",
        "metadata": {"category": "deploy"},
    },
    {
        "doc_id": "postmortem_memory_leak_may",
        "title": "Postmortem: memory leak in worker cache",
        "doc_type": "postmortem",
        "tags": ["memory", "postmortem", "worker"],
        "content": "A stale cache invalidation bug caused sustained memory growth and repeated OOM kills in the worker service until the rollout was reverted.",
        "source": "internal/postmortems/2026-05-memory",
        "metadata": {"category": "memory"},
    },
    {
        "doc_id": "postmortem_db_traffic_spike",
        "title": "Postmortem: traffic spike exhausted DB pool",
        "doc_type": "postmortem",
        "tags": ["database", "traffic", "postmortem"],
        "content": "A traffic spike combined with inefficient query batching exhausted the connection pool and starved new requests.",
        "source": "internal/postmortems/2026-03-db",
        "metadata": {"category": "database"},
    },
    {
        "doc_id": "postmortem_tls_timeout",
        "title": "Postmortem: TLS handshake timeout to payments gateway",
        "doc_type": "postmortem",
        "tags": ["tls", "timeout", "payments"],
        "content": "Handshake failures against the payments provider caused retries and user-facing request timeouts until the provider rotated unhealthy edge nodes.",
        "source": "internal/postmortems/2026-04-tls",
        "metadata": {"category": "network"},
    },
    {
        "doc_id": "runbook_disk_io",
        "title": "Disk I/O saturation playbook",
        "doc_type": "runbook",
        "tags": ["disk", "io", "storage"],
        "content": "Sustained disk I/O wait often presents as broad latency or database slowness. Inspect storage metrics and noisy neighbors before tuning app timeouts.",
        "source": "internal/runbooks/disk-io",
        "metadata": {"category": "storage"},
    },
    {
        "doc_id": "postmortem_bad_feature_flag",
        "title": "Postmortem: feature flag caused cascading errors",
        "doc_type": "postmortem",
        "tags": ["feature-flag", "deploy", "errors"],
        "content": "A newly enabled feature flag triggered unbounded downstream calls, saturating multiple services after deployment completed.",
        "source": "internal/postmortems/2026-01-flag",
        "metadata": {"category": "deploy"},
    },
]


def main() -> None:
    create_db_and_tables()
    with session_scope() as session:
        service = KnowledgeService(session)
        for item in KNOWLEDGE_FIXTURES:
            service.ingest(KnowledgeDocumentCreate(**item))
    print(f"Seeded {len(KNOWLEDGE_FIXTURES)} knowledge documents.")


if __name__ == "__main__":
    main()
