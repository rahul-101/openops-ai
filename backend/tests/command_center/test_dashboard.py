from datetime import UTC, datetime, timedelta

import pytest
from app.domain.entities.incident import IncidentStatus
from app.infrastructure.command_center.dashboard import (
    AiMetrics,
    ExecutionMetrics,
    IncidentMetrics,
    OperationsDashboard,
)
from app.infrastructure.command_center.events import (
    CommandCenterEvent,
    EventType,
)


class StubIncidentService:
    """Minimal stub exposing list_incidents for the dashboard."""

    def __init__(self, incidents):
        self._incidents = incidents

    def list_incidents(self, query):
        from app.domain.models.page import Page

        return Page(
            items=self._incidents,
            total_items=len(self._incidents),
            page=query.page,
            size=query.size,
        )


class StubAgentAnalytics:

    def __init__(self, summary=None):
        self._summary = summary or {
            "total_runs": 10,
            "overall_success_rate": 80.0,
        }

    def get_summary(self):
        return dict(self._summary)


class StubRollback:

    def __init__(self, records):
        self._records = records

    def list(self):
        return list(self._records)


def build_event(
    event_type: EventType,
    *,
    status: str = "success",
    metadata: dict | None = None,
) -> CommandCenterEvent:

    return CommandCenterEvent(
        type=event_type,
        incident_id="inc-1",
        agent="tool",
        action="restart",
        status=status,
        metadata=dict(metadata or {}),
    )


def build_incident(
    status: IncidentStatus,
    *,
    resolved_seconds: int = 0,
):
    from app.domain.entities.incident import Incident

    created = datetime.now(UTC)

    return Incident(
        title="outage",
        description="service down",
        severity="HIGH",
        status=status,
        source="prometheus",
        created_at=created,
        updated_at=created + timedelta(
            seconds=resolved_seconds
        ),
    )


class TestOperationsDashboard:

    def test_incident_metrics_from_service(self):

        incidents = [
            build_incident(IncidentStatus.RESOLVED, resolved_seconds=120),
            build_incident(IncidentStatus.RESOLVED, resolved_seconds=60),
            build_incident(IncidentStatus.OPEN),
        ]

        dashboard = OperationsDashboard(
            incident_service=StubIncidentService(incidents),
        )

        metrics = dashboard.incident_metrics()

        assert metrics.total_incidents == 3

        assert metrics.resolved_incidents == 2

        assert metrics.open_incidents == 1

        assert metrics.auto_resolution_rate == pytest.approx(
            66.666,
            abs=0.01,
        )

        assert metrics.average_resolution_time_s == pytest.approx(
            90.0,
            abs=0.01,
        )

    def test_incident_metrics_no_service(self):

        dashboard = OperationsDashboard()

        metrics = dashboard.incident_metrics()

        assert metrics.total_incidents == 0

        assert metrics.auto_resolution_rate == 0.0

    def test_incident_metrics_empty_service(self):

        dashboard = OperationsDashboard(
            incident_service=StubIncidentService([]),
        )

        metrics = dashboard.incident_metrics()

        assert metrics.total_incidents == 0

        assert metrics.auto_resolution_rate == 0.0

        assert metrics.average_resolution_time_s == 0.0

    def test_ai_metrics_from_analytics(self):

        dashboard = OperationsDashboard(
            agent_analytics=StubAgentAnalytics(),
        )

        metrics = dashboard.ai_metrics()

        assert metrics.total_agent_runs == 10

        assert metrics.agent_success_rate == 80.0

    def test_ai_metrics_tracks_model_usage(self):

        dashboard = OperationsDashboard()

        dashboard.record_ai_usage(
            model="gemini-2.0-flash",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
        )

        dashboard.record_ai_usage(
            model="gemini-2.0-flash",
            input_tokens=50,
            output_tokens=25,
            cost_usd=0.005,
        )

        metrics = dashboard.ai_metrics()

        assert metrics.model_usage == {
            "gemini-2.0-flash": 2,
        }

        assert metrics.input_tokens == 150

        assert metrics.output_tokens == 75

        assert metrics.cost_usd == 0.015

    def test_ai_metrics_records_from_event_metadata(self):

        dashboard = OperationsDashboard()

        dashboard.record_event(
            build_event(
                EventType.DECISION_CREATED,
                metadata={
                    "model": "gemini-2.5-pro",
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "cost_usd": 0.001,
                },
            )
        )

        metrics = dashboard.ai_metrics()

        assert metrics.model_usage == {"gemini-2.5-pro": 1}

        assert metrics.input_tokens == 10

    def test_execution_metrics_from_events(self):

        dashboard = OperationsDashboard()

        dashboard.record_event(
            build_event(
                EventType.TOOL_EXECUTION_COMPLETED,
                status="success",
            )
        )

        dashboard.record_event(
            build_event(
                EventType.TOOL_EXECUTION_COMPLETED,
                status="failure",
            )
        )

        metrics = dashboard.execution_metrics()

        assert metrics.successful_actions == 1

        assert metrics.failed_actions == 1

    def test_execution_metrics_rollback_count(self):

        dashboard = OperationsDashboard(
            rollback=StubRollback(["a", "b"]),
        )

        metrics = dashboard.execution_metrics()

        assert metrics.rollback_count == 2

    def test_snapshot_composes_all_metrics(self):

        incidents = [
            build_incident(IncidentStatus.RESOLVED),
        ]

        dashboard = OperationsDashboard(
            incident_service=StubIncidentService(incidents),
            agent_analytics=StubAgentAnalytics(),
            rollback=StubRollback(["a"]),
        )

        dashboard.record_event(
            build_event(
                EventType.TOOL_EXECUTION_COMPLETED,
                status="success",
            )
        )

        snapshot = dashboard.snapshot()

        assert isinstance(snapshot.incidents, IncidentMetrics)

        assert isinstance(snapshot.ai, AiMetrics)

        assert isinstance(snapshot.execution, ExecutionMetrics)

        assert snapshot.incidents.total_incidents == 1

        assert snapshot.ai.total_agent_runs == 10

        assert snapshot.execution.successful_actions == 1

        assert snapshot.execution.rollback_count == 1

    def test_clear_resets_tracked_state(self):

        dashboard = OperationsDashboard()

        dashboard.record_ai_usage(
            model="flash",
            input_tokens=10,
        )

        dashboard.record_event(
            build_event(
                EventType.TOOL_EXECUTION_COMPLETED,
                status="success",
            )
        )

        dashboard.clear()

        metrics = dashboard.ai_metrics()

        assert metrics.model_usage == {}

        assert metrics.input_tokens == 0

        execution = dashboard.execution_metrics()

        assert execution.successful_actions == 0
