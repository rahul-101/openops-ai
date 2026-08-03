import pytest

from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
)
from app.infrastructure.aiops.event_ingestion import (
    EventSeverity,
    NormalizedEvent,
)
from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.governance.models import RiskLevel
from app.infrastructure.reasoning.confidence import (
    DecisionConfidenceEngine,
)
from app.infrastructure.reasoning.explanation import (
    DecisionExplainer,
)
from app.infrastructure.reasoning.multi_agent import (
    DecisionAgent,
    IncidentAnalysisAgent,
    MultiAgentReasoningRunner,
    RcaAgent,
    ReasoningContext,
    VerificationAgent,
)
from app.infrastructure.reasoning.verification import (
    SelfVerificationLayer,
)


def build_engine() -> AutonomousDecisionEngine:

    risk = RiskBasedExecutor()

    risk.register_action(
        "tool.kubernetes.pod_status",
        RiskLevel.LOW,
    )

    risk.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    return AutonomousDecisionEngine(risk_executor=risk)


def make_event(
    description: str = "pod crash loop",
    severity: EventSeverity = EventSeverity.HIGH,
    tags: list[str] | None = None,
) -> NormalizedEvent:

    return NormalizedEvent(
        event_id="event-1",
        source="kubernetes",
        title="Crash loop",
        description=description,
        severity=severity,
        tags=tags or ["crash"],
    )


def build_runner() -> MultiAgentReasoningRunner:

    return MultiAgentReasoningRunner(
        agents=[
            IncidentAnalysisAgent(engine=build_engine()),
            RcaAgent(),
            VerificationAgent(
                verification=SelfVerificationLayer(),
            ),
            DecisionAgent(
                confidence_engine=DecisionConfidenceEngine(),
                explainer=DecisionExplainer(),
            ),
        ]
    )


@pytest.mark.asyncio
async def test_full_reasoning_flow():

    runner = build_runner()

    context = ReasoningContext(event=make_event())

    results = await runner.run(context)

    names = [result.agent for result in results]

    assert names == [
        "incident_analysis",
        "rca",
        "verification",
        "decision",
    ]

    assert all(
        result.status.value == "success"
        for result in results
    )

    assert context.analysis is not None
    assert context.decision == "restart_service"
    assert context.confidence is not None
    assert context.verification is not None
    assert len(context.reasoning_factors) >= 1
    assert len(context.evidence) >= 1
    assert len(context.alternatives) >= 1

    decision = results[3].output

    assert decision["decision"] == "restart_service"
    assert decision["risk"] in ("low", "medium", "high")
    assert decision["confidence"] > 0
    assert "explanation" in decision
    assert "why" in decision["explanation"]


@pytest.mark.asyncio
async def test_incident_analysis_captures_factors():

    agent = IncidentAnalysisAgent(engine=build_engine())

    context = ReasoningContext(
        event=make_event(
            description="high api error rate and database "
            "timeout detected"
        )
    )

    result = await agent.execute(context)

    assert result.status.value == "success"

    factors = result.output["factors"]

    assert any("error rate" in factor for factor in factors)
    assert any("timeout" in factor for factor in factors)


@pytest.mark.asyncio
async def test_rca_appends_root_cause_factor():

    analysis_context = ReasoningContext(
        event=make_event(),
    )

    incident = IncidentAnalysisAgent(engine=build_engine())

    await incident.execute(analysis_context)

    rca = RcaAgent()

    result = await rca.execute(analysis_context)

    assert result.status.value == "success"
    assert result.output["probable_cause"]
    assert len(result.output["alternatives"]) >= 1

    assert any(
        factor.startswith("root cause identified")
        for factor in analysis_context.reasoning_factors
    )


@pytest.mark.asyncio
async def test_rca_fails_without_analysis():

    rca = RcaAgent()

    context = ReasoningContext(event=make_event())

    result = await rca.execute(context)

    assert result.status.value == "failure"
    assert "No incident analysis" in result.error


@pytest.mark.asyncio
async def test_decision_agent_escalates_when_no_analysis():

    agent = DecisionAgent(
        confidence_engine=DecisionConfidenceEngine(),
        explainer=DecisionExplainer(),
    )

    context = ReasoningContext(event=make_event())

    result = await agent.execute(context)

    assert result.output["decision"] == "escalate_incident"
