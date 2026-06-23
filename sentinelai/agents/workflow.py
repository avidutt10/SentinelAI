from __future__ import annotations

from time import perf_counter

from sqlalchemy.orm import Session

from sentinelai.agents.log_agent import LogAnalysisAgent
from sentinelai.agents.retrieval_agent import RetrievalAgent
from sentinelai.agents.rootcause_agent import RootCauseFixAgent
from sentinelai.core.config import get_settings
from sentinelai.models.db import AgentTrace
from sentinelai.schemas.agent import WorkflowState
from sentinelai.schemas.report import RootCauseReport
from sentinelai.services.knowledge_service import KnowledgeService

settings = get_settings()

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - optional dependency behavior
    StateGraph = None
    START = "START"
    END = "END"


class InvestigationWorkflow:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.log_agent = LogAnalysisAgent()
        self.retrieval_agent = RetrievalAgent(KnowledgeService(db))
        self.rootcause_agent = RootCauseFixAgent()

    def run(self, state: WorkflowState) -> tuple[WorkflowState, list[AgentTrace]]:
        if settings.use_langgraph and StateGraph is not None:
            return self._run_langgraph(state)
        return self._run_sequential(state)

    def _run_sequential(self, state: WorkflowState) -> tuple[WorkflowState, list[AgentTrace]]:
        traces: list[AgentTrace] = []
        analysis = self._timed_agent("log_analysis", state.incident_id, state.model_dump(), lambda: self.log_agent.run(state), traces)
        state.analysis = analysis
        retrieval = self._timed_agent("knowledge_retrieval", state.incident_id, analysis.model_dump(), lambda: self.retrieval_agent.run(state), traces)
        state.retrieval = retrieval
        report = self._timed_agent("root_cause_fix", state.incident_id, retrieval.model_dump(), lambda: self.rootcause_agent.run(state), traces)
        state.report = report
        return state, traces

    def _run_langgraph(self, state: WorkflowState) -> tuple[WorkflowState, list[AgentTrace]]:
        traces: list[AgentTrace] = []
        graph = StateGraph(dict)

        def log_node(data: dict) -> dict:
            workflow_state = WorkflowState.model_validate(data["state"])
            result = self._timed_agent("log_analysis", workflow_state.incident_id, workflow_state.model_dump(), lambda: self.log_agent.run(workflow_state), traces)
            workflow_state.analysis = result
            return {"state": workflow_state.model_dump()}

        def retrieval_node(data: dict) -> dict:
            workflow_state = WorkflowState.model_validate(data["state"])
            result = self._timed_agent("knowledge_retrieval", workflow_state.incident_id, workflow_state.analysis.model_dump(), lambda: self.retrieval_agent.run(workflow_state), traces)
            workflow_state.retrieval = result
            return {"state": workflow_state.model_dump()}

        def rootcause_node(data: dict) -> dict:
            workflow_state = WorkflowState.model_validate(data["state"])
            result = self._timed_agent("root_cause_fix", workflow_state.incident_id, workflow_state.retrieval.model_dump(), lambda: self.rootcause_agent.run(workflow_state), traces)
            workflow_state.report = result
            return {"state": workflow_state.model_dump()}

        graph.add_node("log", log_node)
        graph.add_node("retrieve", retrieval_node)
        graph.add_node("rootcause", rootcause_node)
        graph.add_edge(START, "log")
        graph.add_edge("log", "retrieve")
        graph.add_edge("retrieve", "rootcause")
        graph.add_edge("rootcause", END)
        result = graph.compile().invoke({"state": state.model_dump()})
        return WorkflowState.model_validate(result["state"]), traces

    def _timed_agent(self, name: str, incident_id: int, input_payload: dict, func, traces: list[AgentTrace]):
        started = perf_counter()
        output = func()
        latency_ms = int((perf_counter() - started) * 1000)
        confidence = output.confidence if isinstance(output, RootCauseReport) else None
        summary = getattr(output, "summary", None) or getattr(output, "query", None) or getattr(output, "root_cause", "")
        traces.append(
            AgentTrace(
                incident_id=incident_id,
                agent_name=name,
                status="completed",
                summary=summary,
                input_payload=input_payload,
                output_payload=output.model_dump(),
                confidence=confidence,
                latency_ms=latency_ms,
            )
        )
        return output
