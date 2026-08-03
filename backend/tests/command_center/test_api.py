
import pytest
from app.infrastructure.command_center.command_center import (
    OperationsCommandCenter,
)
from app.infrastructure.command_center.events import (
    EventType,
)
from app.infrastructure.dependencies import (
    get_operations_command_center,
)
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def get_center() -> OperationsCommandCenter:

    return get_operations_command_center()


class TestDashboardApi:

    def test_dashboard_endpoint(self):

        response = client.get("/operations/dashboard")

        assert response.status_code == 200

        body = response.json()

        assert "generated_at" in body

        assert set(body["incidents"]) == {
            "total_incidents",
            "resolved_incidents",
            "open_incidents",
            "auto_resolution_rate",
            "average_resolution_time_s",
        }

        assert set(body["ai"]) == {
            "agent_success_rate",
            "total_agent_runs",
            "model_usage",
            "input_tokens",
            "output_tokens",
            "cost_usd",
        }

        assert set(body["execution"]) == {
            "successful_actions",
            "failed_actions",
            "rollback_count",
        }

    def test_incident_metrics_endpoint(self):

        response = client.get("/operations/metrics/incidents")

        assert response.status_code == 200

        body = response.json()

        assert "total_incidents" in body

        assert "auto_resolution_rate" in body

    def test_ai_metrics_endpoint(self):

        response = client.get("/operations/metrics/ai")

        assert response.status_code == 200

        body = response.json()

        assert "agent_success_rate" in body

        assert "model_usage" in body

    def test_execution_metrics_endpoint(self):

        response = client.get("/operations/metrics/execution")

        assert response.status_code == 200

        body = response.json()

        assert "successful_actions" in body

        assert "rollback_count" in body


class TestTimelineApi:

    def test_timeline_empty_for_unknown_incident(self):

        response = client.get(
            "/incidents/nonexistent/timeline",
        )

        assert response.status_code == 200

        assert response.json() == []

    def test_timeline_returns_recorded_entries(self):

        center = get_center()

        center.emit(
            EventType.ANALYSIS_STARTED,
            incident_id="api-tl-1",
            agent="rca",
            action="analyze",
        )

        response = client.get(
            "/incidents/api-tl-1/timeline",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1

        assert body[0]["agent"] == "rca"

        assert body[0]["action"] == "analyze"


class TestActivityApi:

    def test_activity_snapshot(self):

        response = client.get("/ai/activity")

        assert response.status_code == 200

        body = response.json()

        assert set(body) == {
            "active_agents",
            "current_tasks",
            "completed_actions",
            "failures",
        }


class TestEventsApi:

    def test_list_events(self):

        center = get_center()

        center.emit(
            EventType.INCIDENT_CREATED,
            incident_id="api-ev-1",
            agent="ingestion",
            action="ingest",
        )

        response = client.get("/operations/events")

        assert response.status_code == 200

        body = response.json()

        assert any(
            event["incident_id"] == "api-ev-1"
            for event in body
        )

    def test_list_events_filter_by_type(self):

        response = client.get(
            "/operations/events",
            params={"event_type": "incident_created"},
        )

        assert response.status_code == 200

        body = response.json()

        assert all(
            event["type"] == "incident_created"
            for event in body
        )

    def test_list_events_filter_by_incident(self):

        response = client.get(
            "/operations/events",
            params={"incident_id": "api-ev-1"},
        )

        assert response.status_code == 200

        body = response.json()

        assert all(
            event["incident_id"] == "api-ev-1"
            for event in body
        )


class TestExecutionsApi:

    def test_list_executions(self):

        center = get_center()

        center.monitor_execution(
            "rca",
            task="analyze",
            incident_id="api-ex-1",
        )

        response = client.get(
            "/operations/executions",
            params={"incident_id": "api-ex-1"},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["summary"]["total"] >= 1

        assert body["executions"][0]["incident_id"] == "api-ex-1"

    def test_get_execution_by_id(self):

        center = get_center()

        execution = center.monitor_execution(
            "rca",
            task="analyze",
        )

        response = client.get(
            f"/operations/executions/{execution.execution_id}",
        )

        assert response.status_code == 200

        body = response.json()

        assert body["execution_id"] == execution.execution_id

    def test_get_execution_missing_returns_404(self):

        response = client.get(
            "/operations/executions/does-not-exist",
        )

        assert response.status_code == 404


class TestSseApi:

    @pytest.mark.asyncio
    async def test_stream_receives_emitted_event(self):

        import asyncio

        from app.api.routes.command_center import stream_events

        center = get_center()

        response = await stream_events(center)

        generator = response.body_iterator

        async def emit():
            await asyncio.sleep(0.05)

            center.emit(
                EventType.ANALYSIS_STARTED,
                incident_id="api-sse-1",
                agent="rca",
                action="analyze",
            )

        task = asyncio.create_task(emit())

        chunk = await asyncio.wait_for(
            anext(generator),
            timeout=3.0,
        )

        await task

        assert "api-sse-1" in chunk

        assert "analysis_started" in chunk

    @pytest.mark.asyncio
    async def test_stream_emits_keep_alive_when_idle(self):

        import asyncio

        from app.api.routes.command_center import stream_events

        center = get_center()

        response = await stream_events(center)

        generator = response.body_iterator

        chunk = await asyncio.wait_for(
            anext(generator),
            timeout=20.0,
        )

        assert chunk == ": keep-alive\n\n"

    @pytest.mark.asyncio
    async def test_stream_closes_cleanly(self):


        from app.api.routes.command_center import stream_events

        center = get_center()

        response = await stream_events(center)

        generator = response.body_iterator

        await generator.aclose()

