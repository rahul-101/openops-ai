import pytest
from app.infrastructure.command_center.execution_monitor import (
    AgentExecution,
    ExecutionMonitor,
    ExecutionStatus,
)


class TestExecutionMonitor:

    def test_start_tracks_running(self):

        monitor = ExecutionMonitor()

        execution = monitor.start("rca", task="analyze")

        assert execution.status == ExecutionStatus.RUNNING

        assert monitor.get(execution.execution_id) is execution

    def test_complete_marks_success(self):

        monitor = ExecutionMonitor()

        execution = monitor.start("tool", task="restart")

        monitor.complete(
            execution.execution_id,
            success=True,
            duration_ms=12.5,
        )

        assert execution.status == ExecutionStatus.COMPLETED

        assert execution.duration_ms == 12.5

        assert execution.completion_time is not None

    def test_complete_marks_failure(self):

        monitor = ExecutionMonitor()

        execution = monitor.start("tool", task="restart")

        monitor.complete(
            execution.execution_id,
            success=False,
            error="connection refused",
        )

        assert execution.status == ExecutionStatus.FAILED

        assert execution.error == "connection refused"

    def test_fail_shortcut(self):

        monitor = ExecutionMonitor()

        execution = monitor.start("tool", task="rollback")

        monitor.fail(execution.execution_id, error="timeout")

        assert execution.status == ExecutionStatus.FAILED

        assert execution.error == "timeout"

    def test_complete_missing_execution_raises(self):

        monitor = ExecutionMonitor()

        with pytest.raises(KeyError):
            monitor.complete("missing", success=True)

    def test_get_missing_returns_none(self):

        monitor = ExecutionMonitor()

        assert monitor.get("missing") is None

    def test_list_filters_by_status(self):

        monitor = ExecutionMonitor()

        ok = monitor.start("a")

        bad = monitor.start("b")

        monitor.complete(ok.execution_id, success=True)

        monitor.complete(bad.execution_id, success=False)

        completed = monitor.list(
            status=ExecutionStatus.COMPLETED,
        )

        assert [e.execution_id for e in completed] == [
            ok.execution_id,
        ]

    def test_list_filters_by_incident(self):

        monitor = ExecutionMonitor()

        first = monitor.start("a", incident_id="inc-1")

        monitor.start("b", incident_id="inc-2")

        filtered = monitor.list(incident_id="inc-1")

        assert [e.execution_id for e in filtered] == [
            first.execution_id,
        ]

    def test_summary_counts(self):

        monitor = ExecutionMonitor()

        monitor.start("a")

        ok = monitor.start("b")

        bad = monitor.start("c")

        monitor.complete(ok.execution_id, success=True)

        monitor.complete(bad.execution_id, success=False)

        summary = monitor.summary()

        assert summary["total"] == 3

        assert summary["running"] == 1

        assert summary["completed"] == 1

        assert summary["failed"] == 1

        assert summary["success_rate"] == 50.0

    def test_summary_empty(self):

        monitor = ExecutionMonitor()

        summary = monitor.summary()

        assert summary["total"] == 0

        assert summary["success_rate"] == 0.0

    def test_clear(self):

        monitor = ExecutionMonitor()

        monitor.start("a")

        monitor.clear()

        assert monitor.summary()["total"] == 0

    def test_to_dict_shape(self):

        execution = AgentExecution(
            agent="tool",
            task="restart",
            incident_id="inc-1",
        )

        payload = execution.to_dict()

        assert payload["agent"] == "tool"

        assert payload["task"] == "restart"

        assert payload["incident_id"] == "inc-1"

        assert payload["status"] == "running"

        assert "execution_id" in payload

        assert "start_time" in payload
