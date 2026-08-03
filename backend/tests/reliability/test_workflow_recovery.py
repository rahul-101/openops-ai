import pytest

from app.infrastructure.reliability.workflow_recovery import (
    RecoveryStatus,
    WorkflowRecovery,
)


def test_begin_workflow():

    recovery = WorkflowRecovery()

    record = recovery.begin(
        workflow_id="wf-1",
        steps=["alpha", "beta", "gamma"],
    )

    assert record.workflow_id == "wf-1"
    assert record.status == RecoveryStatus.IN_PROGRESS
    assert list(record.steps.keys()) == [
        "alpha",
        "beta",
        "gamma",
    ]


def test_checkpoint_records_success():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha", "beta"],
    )

    checkpoint = recovery.checkpoint(
        "wf-1",
        "alpha",
        output={"result": "ok"},
    )

    assert checkpoint.step == "alpha"

    record = recovery.get("wf-1")

    assert record.completed_steps == ["alpha"]

    state = recovery.get_step("wf-1", "alpha")

    assert state.succeeded is True
    assert state.output == {"result": "ok"}


def test_retry_limits():

    recovery = WorkflowRecovery(max_retries=2)

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha"],
    )

    assert recovery.can_retry("wf-1", "alpha") is True

    recovery.record_failure("wf-1", "alpha")

    assert recovery.can_retry("wf-1", "alpha") is True

    recovery.record_failure("wf-1", "alpha")

    assert recovery.can_retry("wf-1", "alpha") is True

    recovery.record_failure("wf-1", "alpha")

    assert recovery.can_retry("wf-1", "alpha") is False

    state = recovery.get_step("wf-1", "alpha")

    assert state.attempts == 3
    assert state.failed is True


def test_resume_returns_remaining_steps():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha", "beta", "gamma"],
    )

    recovery.checkpoint("wf-1", "alpha")

    remaining = recovery.resume("wf-1")

    assert remaining == ["beta", "gamma"]


def test_get_checkpoint_last_completed():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha", "beta"],
    )

    recovery.checkpoint("wf-1", "alpha")
    recovery.checkpoint("wf-1", "beta")

    checkpoint = recovery.get_checkpoint("wf-1")

    assert checkpoint.step == "beta"
    assert checkpoint.state["completed_steps"] == [
        "alpha",
        "beta",
    ]


def test_get_checkpoint_none_before_any():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha"],
    )

    assert recovery.get_checkpoint("wf-1") is None


def test_complete_marks_status():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha"],
    )

    record = recovery.complete("wf-1")

    assert record.status == RecoveryStatus.COMPLETED


def test_rollback_clears_progress():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha", "beta"],
    )

    recovery.checkpoint("wf-1", "alpha")

    record = recovery.rollback("wf-1")

    assert record.status == RecoveryStatus.FAILED
    assert record.completed_steps == []

    state = recovery.get_step("wf-1", "alpha")

    assert state.succeeded is False


def test_missing_workflow_raises():

    recovery = WorkflowRecovery()

    with pytest.raises(KeyError):
        recovery.checkpoint("missing", "alpha")


def test_clear():

    recovery = WorkflowRecovery()

    recovery.begin(
        workflow_id="wf-1",
        steps=["alpha"],
    )

    recovery.clear()

    assert recovery.list() == []
