from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
)
from app.infrastructure.aiops.event_ingestion import (
    EventSeverity,
    NormalizedEvent,
)
from app.infrastructure.aiops.playbook_engine import (
    Playbook,
    PlaybookStep,
)
from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)


def make_engine() -> AutonomousDecisionEngine:

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


def make_event(description: str = "pod crash loop") -> NormalizedEvent:

    return NormalizedEvent(
        event_id="event-1",
        source="kubernetes",
        title="Crash loop",
        description=description,
        severity=EventSeverity.HIGH,
        tags=["crash"],
    )


def make_playbook() -> Playbook:

    return Playbook(
        name="crash_restart",
        steps=[
            PlaybookStep(
                name="check",
                tool="kubernetes",
                action="pod_status",
                risk_level="low",
            ),
            PlaybookStep(
                name="restart",
                tool="kubernetes",
                action="restart",
                risk_level="medium",
            ),
        ],
    )


def test_analyze_diagnoses_crash():

    engine = make_engine()

    analysis = engine.analyze(make_event())

    assert analysis.incident_id == "event-1"
    assert "crash" in analysis.probable_cause.lower()
    assert analysis.confidence >= 0.7


def test_analyze_diagnoses_cpu():

    engine = make_engine()

    analysis = engine.analyze(
        make_event(description="cpu usage is 95 percent")
    )

    assert "cpu" in analysis.probable_cause.lower()
    assert analysis.category == "infrastructure"


def test_analyze_diagnoses_memory():

    engine = make_engine()

    analysis = engine.analyze(
        make_event(description="memory exhaustion on node")
    )

    assert "memory" in analysis.probable_cause.lower()
    assert analysis.confidence == 0.7


def test_analyze_unknown_low_confidence():

    engine = make_engine()

    analysis = engine.analyze(
        make_event(description="mysterious issue")
    )

    assert analysis.confidence == 0.3
    assert "escalate" in analysis.recommendation.lower()


def test_decide_selects_playbook_actions():

    engine = make_engine()

    decision = engine.decide(
        make_event(),
        make_playbook(),
    )

    assert decision.incident_id == "event-1"
    assert decision.playbook == "crash_restart"
    assert len(decision.actions) == 2

    check, restart = decision.actions

    assert check.tool == "kubernetes"
    assert check.action == "pod_status"
    assert check.approved is True

    assert restart.action == "restart"
    assert restart.decision == ActionDecision.APPROVAL_REQUIRED
    assert restart.approved is False


def test_decide_no_playbook_has_no_actions():

    engine = make_engine()

    decision = engine.decide(
        make_event(),
        None,
    )

    assert decision.actions == []
    assert decision.can_auto_execute is False


def test_can_auto_execute_all_approved():

    engine = make_engine()

    playbook = Playbook(
        name="read_only",
        steps=[
            PlaybookStep(
                name="check",
                tool="kubernetes",
                action="pod_status",
                risk_level="low",
            )
        ],
    )

    decision = engine.decide(
        make_event(),
        playbook,
    )

    assert decision.can_auto_execute is True
