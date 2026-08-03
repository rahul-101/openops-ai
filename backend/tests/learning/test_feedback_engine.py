from app.infrastructure.learning.feedback_engine import (
    FeedbackEngine,
)

import pytest


def test_record_outcome_success():

    engine = FeedbackEngine()

    entry = engine.record_outcome(
        recommendation_id="rec-1",
        outcome="success",
        incident_id="inc-1",
        agent="triage-agent",
        model="gpt-4o",
    )

    assert entry.id
    assert entry.recommendation_id == "rec-1"
    assert entry.outcome == "success"
    assert entry.incident_id == "inc-1"
    assert entry.agent == "triage-agent"
    assert entry.model == "gpt-4o"


def test_record_human_feedback_updates_entry():

    engine = FeedbackEngine()

    engine.record_outcome(
        recommendation_id="rec-1",
        outcome="failure",
    )

    entry = engine.record_human_feedback(
        recommendation_id="rec-1",
        feedback="wrong RCA",
        outcome="failure",
    )

    assert entry.human_feedback == "wrong RCA"
    assert entry.outcome == "failure"

    entries = engine.list()

    assert len(entries) == 1
    assert entries[0].human_feedback == "wrong RCA"


def test_record_human_feedback_creates_entry_when_missing():

    engine = FeedbackEngine()

    entry = engine.record_human_feedback(
        recommendation_id="rec-9",
        feedback="great work",
    )

    assert entry.recommendation_id == "rec-9"
    assert entry.human_feedback == "great work"
    assert entry.outcome == "unknown"


def test_list_filters_by_outcome():

    engine = FeedbackEngine()

    engine.record_outcome(
        recommendation_id="rec-1",
        outcome="success",
    )

    engine.record_outcome(
        recommendation_id="rec-2",
        outcome="failure",
    )

    successes = engine.list(outcome="success")

    assert len(successes) == 1
    assert successes[0].recommendation_id == "rec-1"


def test_list_filters_by_incident():

    engine = FeedbackEngine()

    engine.record_outcome(
        recommendation_id="rec-1",
        outcome="success",
        incident_id="inc-1",
    )

    engine.record_outcome(
        recommendation_id="rec-2",
        outcome="failure",
        incident_id="inc-2",
    )

    entries = engine.list(incident_id="inc-1")

    assert len(entries) == 1
    assert entries[0].recommendation_id == "rec-1"


def test_get_stats_empty():

    engine = FeedbackEngine()

    stats = engine.get_stats()

    assert stats["total"] == 0
    assert stats["success_rate"] == 0.0


def test_get_stats_counts():

    engine = FeedbackEngine()

    engine.record_outcome(
        recommendation_id="rec-1",
        outcome="success",
    )

    engine.record_outcome(
        recommendation_id="rec-2",
        outcome="success",
    )

    engine.record_outcome(
        recommendation_id="rec-3",
        outcome="failure",
    )

    stats = engine.get_stats()

    assert stats["total"] == 3
    assert stats["successes"] == 2
    assert stats["failures"] == 1
    assert stats["success_rate"] == pytest.approx(66.67, abs=0.01)


def test_clear():

    engine = FeedbackEngine()

    engine.record_outcome(
        recommendation_id="rec-1",
        outcome="success",
    )

    engine.clear()

    assert engine.list() == []
