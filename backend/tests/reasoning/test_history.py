from app.infrastructure.reasoning.history import (
    ReasoningHistoryRecord,
    ReasoningHistoryStore,
)


def test_record_and_get():

    history = ReasoningHistoryStore()

    record = history.record(
        incident_id="inc-1",
        agents_involved=[
            "incident_analysis",
            "rca",
            "verification",
            "decision",
        ],
        decisions=["restart_service"],
        confidence=0.94,
        risk="low",
        outcome="approved",
        explanation={
            "why": "high error rate",
            "evidence": ["error rate 45%"],
        },
    )

    assert isinstance(record, ReasoningHistoryRecord)

    fetched = history.get("inc-1")

    assert fetched is not None
    assert fetched.incident_id == "inc-1"
    assert fetched.decisions == ["restart_service"]
    assert fetched.confidence == 0.94
    assert fetched.outcome == "approved"
    assert fetched.agents_involved[0] == "incident_analysis"


def test_update_outcome():

    history = ReasoningHistoryStore()

    history.record(
        incident_id="inc-1",
        agents_involved=["rca"],
        decisions=["restart_service"],
        confidence=0.9,
        risk="low",
    )

    updated = history.update_outcome(
        "inc-1",
        "executed",
    )

    assert updated is not None
    assert updated.outcome == "executed"


def test_update_outcome_missing_returns_none():

    history = ReasoningHistoryStore()

    assert history.update_outcome("missing", "executed") is None


def test_list_and_limit():

    history = ReasoningHistoryStore()

    for index in range(3):
        history.record(
            incident_id=f"inc-{index}",
            agents_involved=["rca"],
            decisions=["monitor_only"],
            confidence=0.5,
            risk="low",
        )

    all_records = history.list()

    assert len(all_records) == 3

    limited = history.list(limit=2)

    assert len(limited) == 2


def test_list_by_outcome():

    history = ReasoningHistoryStore()

    history.record(
        incident_id="inc-1",
        agents_involved=["rca"],
        decisions=["restart_service"],
        confidence=0.9,
        risk="low",
        outcome="approved",
    )

    history.record(
        incident_id="inc-2",
        agents_involved=["rca"],
        decisions=["escalate_incident"],
        confidence=0.5,
        risk="medium",
        outcome="pending_review",
    )

    approved = history.list_by_outcome("approved")

    assert [r.incident_id for r in approved] == ["inc-1"]


def test_get_missing_returns_none():

    history = ReasoningHistoryStore()

    assert history.get("missing") is None


def test_clear():

    history = ReasoningHistoryStore()

    history.record(
        incident_id="inc-1",
        agents_involved=["rca"],
        decisions=["monitor_only"],
        confidence=0.5,
        risk="low",
    )

    history.clear()

    assert history.list() == []
