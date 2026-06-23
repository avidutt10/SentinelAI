from __future__ import annotations

from sentinelai.schemas.agent import RetrievalAgentResult, WorkflowState
from sentinelai.services.knowledge_service import KnowledgeService


class RetrievalAgent:
    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    def run(self, state: WorkflowState) -> RetrievalAgentResult:
        analysis = state.analysis
        assert analysis is not None
        query = " ".join(
            [
                state.title,
                state.service or "",
                " ".join(analysis.anomalies),
                " ".join(analysis.affected_services),
                analysis.summary,
            ]
        ).strip()
        matches = self.knowledge_service.retrieve(query=query, top_k=3)
        return RetrievalAgentResult(query=query, matches=matches)
