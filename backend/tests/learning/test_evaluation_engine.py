import pytest

from app.infrastructure.learning.evaluation_engine import (
    EvaluationEngine,
)


def test_record_evaluation():

    engine = EvaluationEngine()

    record = engine.record_evaluation(
        incident_id="inc-1",
        rca_accurate=True,
        remediation_success=True,
        resolution_time_ms=120_000,
        confidence=0.9,
    )

    assert record.id
    assert record.incident_id == "inc-1"
    assert record.rca_accurate is True
    assert record.remediation_success is True
    assert record.resolution_time_ms == 120_000
    assert record.confidence == 0.9
    assert record.outcome is True


def test_outcome_defaults_to_false_when_any_missing():

    engine = EvaluationEngine()

    record = engine.record_evaluation(
        incident_id="inc-1",
        rca_accurate=True,
        remediation_success=False,
    )

    assert record.outcome is False


def test_record_confidence():

    engine = EvaluationEngine()

    record = engine.record_confidence(
        incident_id="inc-1",
        confidence=0.9,
        outcome=True,
    )

    assert record.confidence == 0.9
    assert record.outcome is True


def test_get_stats_empty():

    engine = EvaluationEngine()

    stats = engine.get_stats()

    assert stats["total"] == 0
    assert stats["rca_accuracy"] == 0.0
    assert stats["confidence_accuracy"] == 0.0


def test_get_stats_rca_and_remediation():

    engine = EvaluationEngine()

    engine.record_evaluation(
        incident_id="inc-1",
        rca_accurate=True,
        remediation_success=True,
    )

    engine.record_evaluation(
        incident_id="inc-2",
        rca_accurate=True,
        remediation_success=False,
    )

    stats = engine.get_stats()

    assert stats["total"] == 2
    assert stats["rca_accuracy"] == 100.0
    assert stats["remediation_success_rate"] == 50.0


def test_get_stats_average_resolution_time():

    engine = EvaluationEngine()

    engine.record_evaluation(
        incident_id="inc-1",
        rca_accurate=True,
        remediation_success=True,
        resolution_time_ms=100_000,
    )

    engine.record_evaluation(
        incident_id="inc-2",
        rca_accurate=True,
        remediation_success=True,
        resolution_time_ms=300_000,
    )

    stats = engine.get_stats()

    assert stats["average_resolution_time_ms"] == 200_000


def test_get_stats_confidence_accuracy():

    engine = EvaluationEngine()

    engine.record_confidence(
        incident_id="inc-1",
        confidence=0.9,
        outcome=True,
    )

    engine.record_confidence(
        incident_id="inc-2",
        confidence=0.8,
        outcome=True,
    )

    engine.record_confidence(
        incident_id="inc-3",
        confidence=0.9,
        outcome=False,
    )

    stats = engine.get_stats()

    assert stats["average_confidence"] == pytest.approx(
        (0.9 + 0.8 + 0.9) / 3
    )
    assert stats["confidence_accuracy"] == pytest.approx(
        (2 / 3) * 100
    )


def test_list_filters_by_incident():

    engine = EvaluationEngine()

    engine.record_evaluation(
        incident_id="inc-1",
        rca_accurate=True,
        remediation_success=True,
    )

    engine.record_evaluation(
        incident_id="inc-2",
        rca_accurate=True,
        remediation_success=True,
    )

    records = engine.list(incident_id="inc-1")

    assert len(records) == 1
    assert records[0].incident_id == "inc-1"


def test_clear():

    engine = EvaluationEngine()

    engine.record_evaluation(
        incident_id="inc-1",
        rca_accurate=True,
        remediation_success=True,
    )

    engine.clear()

    assert engine.list() == []
