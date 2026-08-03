from unittest.mock import AsyncMock

import pytest

from app.application.agents.agent_registry import AgentRegistry
from app.application.dto.responses.ai_response import AIResponse
from app.application.orchestration.agent_orchestrator import (
    AgentOrchestrator,
)
from app.application.workflows.incident_workflow import (
    IncidentWorkflow,
)
from app.application.workflows.workflow_engine import (
    WorkflowEngine,
)
from app.domain.entities.incident_workflow_state import (
    WorkflowExecutionStatus,
)
from app.infrastructure.ai.agents.analysis_agent import (
    AnalysisAgent,
)
from app.infrastructure.ai.agents.recommendation_agent import (
    RecommendationAgent,
)
from app.infrastructure.ai.agents.triage_agent import (
    TriageAgent,
)


def build_workflow(ai_service) -> IncidentWorkflow:

    registry = AgentRegistry()

    registry.register(TriageAgent())

    registry.register(
        AnalysisAgent(
            ai_service=ai_service,
        )
    )

    registry.register(RecommendationAgent())

    orchestrator = AgentOrchestrator(registry)

    engine = WorkflowEngine(orchestrator)

    return IncidentWorkflow(
        engine=engine,
        registry=registry,
    )


def build_ai_service() -> AsyncMock:

    service = AsyncMock()

    service.analyze_incident.return_value = AIResponse(
        summary="Database timeouts detected",
        severity="High",
        category="Database",
        probable_cause="Connection pool exhaustion",
        recommendation="Increase connection pool size",
        confidence=0.9,
        provider="gemini",
        model="gemini-2.0-flash",
        input_tokens=120,
        output_tokens=40,
    )

    return service


@pytest.mark.asyncio
async def test_incident_workflow_execution():

    ai_service = build_ai_service()

    workflow = build_workflow(ai_service)

    state = await workflow.run(
        incident_id="inc-1",
        input_data={
            "title": "DB connection timeouts",
            "description": "Database timeout under load",
            "severity": "High",
        },
    )

    assert state.incident_id == "inc-1"
    assert state.workflow_status == (
        WorkflowExecutionStatus.COMPLETED
    )

    assert state.current_step == "recommendation"

    assert [entry.agent for entry in state.agent_history] == [
        "triage",
        "analysis",
        "recommendation",
    ]

    assert all(
        entry.status == "success"
        for entry in state.agent_history
    )

    assert state.execution_result["category"] == "database"

    assert (
        "Increase connection pool size"
        in state.recommendations
    )

    assert (
        state.execution_result["final_recommendations"]
        == state.recommendations
    )

    ai_service.analyze_incident.assert_awaited_once()


@pytest.mark.asyncio
async def test_incident_workflow_reports_failure():

    ai_service = build_ai_service()

    ai_service.analyze_incident.side_effect = (
        RuntimeError("provider down")
    )

    workflow = build_workflow(ai_service)

    state = await workflow.run(
        incident_id="inc-1",
        input_data={
            "title": "DB connection timeouts",
            "description": "Database timeout under load",
            "severity": "High",
        },
    )

    assert state.workflow_status == (
        WorkflowExecutionStatus.FAILED
    )

    analysis_entry = next(
        entry
        for entry in state.agent_history
        if entry.agent == "analysis"
    )

    assert analysis_entry.status == "failure"
    assert analysis_entry.error == "provider down"
