import asyncio

import pytest
from app.infrastructure.command_center.command_center import (
    OperationsCommandCenter,
)
from app.infrastructure.command_center.events import (
    EventType,
)


class TestOperationsCommandCenter:

    def test_emit_returns_event_and_records_history(self):

        center = OperationsCommandCenter()

        event = center.emit(
            EventType.INCIDENT_CREATED,
            incident_id="inc-1",
            agent="ingestion",
            action="ingest",
            status="success",
        )

        history = center.history()

        assert len(history) == 1

        assert history[0].event_id == event.event_id

    def test_emit_writes_timeline_entry(self):

        center = OperationsCommandCenter()

        center.emit(
            EventType.ANALYSIS_STARTED,
            incident_id="inc-1",
            agent="rca",
            action="analyze",
        )

        center.emit(
            EventType.DECISION_CREATED,
            incident_id="inc-1",
            agent="planner",
            action="restart",
            status="success",
        )

        timeline = center.get_timeline("inc-1")

        assert len(timeline) == 2

        assert timeline[0].agent == "rca"

        assert timeline[1].agent == "planner"

    def test_tool_started_tracks_activity_and_execution(self):

        center = OperationsCommandCenter()

        center.emit(
            EventType.TOOL_EXECUTION_STARTED,
            incident_id="inc-1",
            agent="k8s",
            action="restart",
        )

        snapshot = center.activity_snapshot()

        assert snapshot.active_agents == ["k8s"]

        assert center.executions(
            incident_id="inc-1"
        )[0].status.value == "running"

    def test_tool_completed_updates_activity_and_dashboard(self):

        center = OperationsCommandCenter()

        center.emit(
            EventType.TOOL_EXECUTION_STARTED,
            incident_id="inc-1",
            agent="k8s",
            action="restart",
        )

        center.emit(
            EventType.TOOL_EXECUTION_COMPLETED,
            incident_id="inc-1",
            agent="k8s",
            action="restart",
            status="success",
            duration_ms=100.0,
        )

        snapshot = center.activity_snapshot()

        assert snapshot.completed_actions == 1

        execution = center.executions()[0]

        assert execution.status.value == "completed"

        metrics = center.dashboard.execution_metrics()

        assert metrics.successful_actions == 1

    def test_monitor_and_complete_execution_helpers(self):

        center = OperationsCommandCenter()

        execution = center.monitor_execution(
            "rca",
            task="analyze",
            incident_id="inc-1",
        )

        center.complete_execution(
            execution.execution_id,
            success=True,
            duration_ms=42.0,
        )

        assert execution.status.value == "completed"

        assert execution.duration_ms == 42.0

    def test_dashboard_snapshot_shape(self):

        center = OperationsCommandCenter()

        snapshot = center.dashboard_snapshot()

        assert snapshot.incidents.total_incidents >= 0

        assert snapshot.ai.total_agent_runs >= 0

        assert snapshot.execution.successful_actions >= 0

    def test_failure_event_tracks_failure(self):

        center = OperationsCommandCenter()

        center.emit(
            EventType.TOOL_EXECUTION_STARTED,
            incident_id="inc-1",
            agent="k8s",
            action="restart",
        )

        center.emit(
            EventType.TOOL_EXECUTION_COMPLETED,
            incident_id="inc-1",
            agent="k8s",
            action="restart",
            status="failure",
        )

        snapshot = center.activity_snapshot()

        assert snapshot.failures == 1

        metrics = center.dashboard.execution_metrics()

        assert metrics.failed_actions == 1


@pytest.mark.asyncio
class TestCommandCenterStreaming:

    async def test_stream_receives_emitted_event(self):

        center = OperationsCommandCenter()

        stream = center.open_stream()

        center.emit(
            EventType.INCIDENT_CREATED,
            incident_id="inc-x",
            agent="ingestion",
        )

        payload = await asyncio.wait_for(
            stream.get(),
            timeout=1.0,
        )

        assert payload["incident_id"] == "inc-x"

        assert payload["type"] == "incident_created"

        center.close_stream(stream)

    async def test_multiple_events_preserved_in_order(self):

        center = OperationsCommandCenter()

        stream = center.open_stream()

        for i in range(3):
            center.emit(
                EventType.RCA_COMPLETED,
                incident_id="inc-1",
                action=f"step-{i}",
            )

        actions = []

        for _ in range(3):
            payload = await asyncio.wait_for(
                stream.get(),
                timeout=1.0,
            )

            actions.append(payload["action"])

        assert actions == ["step-0", "step-1", "step-2"]

        center.close_stream(stream)
