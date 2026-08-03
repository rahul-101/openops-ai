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
from app.infrastructure.reasoning.history import (
    ReasoningHistoryStore,
)
from app.infrastructure.reasoning.model_selection import (
    DynamicModelSelector,
)
from app.infrastructure.reasoning.multi_agent import (
    DecisionAgent,
    IncidentAnalysisAgent,
    MultiAgentReasoningRunner,
    RcaAgent,
    VerificationAgent,
)
from app.infrastructure.reasoning.orchestrator import (
    ReasoningOrchestrator,
)
from app.infrastructure.reasoning.verification import (
    SelfVerificationLayer,
)


def build_orchestrator() -> ReasoningOrchestrator:

    risk = RiskBasedExecutor()

    risk.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    engine = AutonomousDecisionEngine(risk_executor=risk)

    runner = MultiAgentReasoningRunner(
        agents=[
            IncidentAnalysisAgent(engine=engine),
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

    selector = DynamicModelSelector()

    selector.register_simple_model(
        name="flash",
        model="gemini-2.0-flash",
        provider="gemini",
    )

    selector.register_complex_model(
        name="pro",
        model="gemini-2.5-pro",
        provider="gemini",
    )

    return ReasoningOrchestrator(
        runner=runner,
        history=ReasoningHistoryStore(),
        model_selector=selector,
    )


@pytest.mark.asyncio
async def test_orchestrator_produces_full_report():

    orchestrator = build_orchestrator()

    event = NormalizedEvent(
        event_id="inc-42",
        source="kubernetes",
        title="Crash loop",
        description="pod crash loop with database timeout "
        "requires root cause recovery",
        severity=EventSeverity.HIGH,
        tags=["crash", "database"],
    )

    report = await orchestrator.reason(event)

    assert report.incident_id == "inc-42"
    assert report.decision == "restart_service"
    assert report.confidence > 0
    assert report.risk in ("low", "medium", "high")
    assert len(report.reasoning) >= 1
    assert len(report.evidence) >= 1
    assert len(report.alternatives) >= 1
    assert report.validated in (True, False)
    assert report.agents_involved == [
        "incident_analysis",
        "rca",
        "verification",
        "decision",
    ]
    assert report.explanation["why"]
    assert report.model_selection["model"] == "gemini-2.5-pro"
    assert report.history_id == "inc-42"


@pytest.mark.asyncio
async def test_orchestrator_persists_history():

    orchestrator = build_orchestrator()

    event = NormalizedEvent(
        event_id="inc-7",
        source="kubernetes",
        title="Memory pressure",
        description="pod memory pressure with crash loop",
        severity=EventSeverity.MEDIUM,
        tags=["memory"],
    )

    report = await orchestrator.reason(event)

    record = orchestrator.get_history("inc-7")

    assert record is not None
    assert record.incident_id == "inc-7"
    assert record.decisions == [report.decision]
    assert record.confidence == report.confidence
    assert record.outcome in (
        "approved",
        "pending_review",
    )

    history = orchestrator.list_history()

    assert any(
        item.incident_id == "inc-7" for item in history
    )


@pytest.mark.asyncio
async def test_simple_incident_uses_cheap_model():

    orchestrator = build_orchestrator()

    event = NormalizedEvent(
        event_id="inc-8",
        source="kubernetes",
        title="Log rotation",
        description="routine log rotation completed",
        severity=EventSeverity.LOW,
        tags=["info"],
    )

    report = await orchestrator.reason(event)

    assert report.model_selection["model"] == "gemini-2.0-flash"
