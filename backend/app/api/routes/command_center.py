import asyncio
import json

from app.infrastructure.command_center.command_center import (
    OperationsCommandCenter,
)
from app.infrastructure.command_center.events import (
    EventType,
)
from app.infrastructure.dependencies import (
    get_operations_command_center,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter(
    tags=["Operations Command Center"],
)


# ==========================================================
# Real-Time Event Streaming (SSE)
# ==========================================================


@router.get(
    "/operations/events/stream",
    summary="Stream real-time operations events (SSE)",
)
async def stream_events(
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    stream = command_center.open_stream()

    async def event_generator():

        try:

            while True:

                try:

                    payload = await asyncio.wait_for(
                        stream.get(),
                        timeout=15.0,
                    )

                    yield (
                        f"data: {json.dumps(payload)}\n\n"
                    )

                except TimeoutError:

                    yield ": keep-alive\n\n"

        finally:

            command_center.close_stream(stream)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/operations/events",
    summary="List recent operations events",
)
def list_events(
    limit: int = Query(50, ge=1, le=500),
    event_type: EventType | None = None,
    incident_id: str | None = None,
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    events = command_center.history(
        limit,
        event_type=event_type,
        incident_id=incident_id,
    )

    return [event.to_dict() for event in events]


# ==========================================================
# Incident Timeline
# ==========================================================


@router.get(
    "/incidents/{incident_id}/timeline",
    summary="Get the timeline for an incident",
)
def get_incident_timeline(
    incident_id: str,
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    entries = command_center.get_timeline(incident_id)

    return [entry.to_dict() for entry in entries]


# ==========================================================
# AI Activity Feed
# ==========================================================


@router.get(
    "/ai/activity",
    summary="Get the AI activity feed snapshot",
)
def get_ai_activity(
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    snapshot = command_center.activity_snapshot()

    return {
        "active_agents": snapshot.active_agents,
        "current_tasks": snapshot.current_tasks,
        "completed_actions": snapshot.completed_actions,
        "failures": snapshot.failures,
    }


# ==========================================================
# Agent Execution Monitoring
# ==========================================================


@router.get(
    "/operations/executions",
    summary="List tracked agent executions",
)
def list_executions(
    incident_id: str | None = None,
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    executions = command_center.executions(
        incident_id=incident_id,
    )

    return {
        "summary": command_center.monitor.summary(),
        "executions": [
            execution.to_dict()
            for execution in executions
        ],
    }


@router.get(
    "/operations/executions/{execution_id}",
    summary="Get a single tracked execution",
)
def get_execution(
    execution_id: str,
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    execution = command_center.monitor.get(execution_id)

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found.",
        )

    return execution.to_dict()


# ==========================================================
# Operations Dashboard
# ==========================================================


@router.get(
    "/operations/dashboard",
    summary="Get the full operations dashboard snapshot",
)
def get_dashboard(
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    snapshot = command_center.dashboard_snapshot()

    return {
        "generated_at": snapshot.generated_at.isoformat(),
        "incidents": {
            "total_incidents": (
                snapshot.incidents.total_incidents
            ),
            "resolved_incidents": (
                snapshot.incidents.resolved_incidents
            ),
            "open_incidents": (
                snapshot.incidents.open_incidents
            ),
            "auto_resolution_rate": round(
                snapshot.incidents.auto_resolution_rate,
                2,
            ),
            "average_resolution_time_s": round(
                snapshot.incidents.average_resolution_time_s,
                2,
            ),
        },
        "ai": {
            "agent_success_rate": (
                snapshot.ai.agent_success_rate
            ),
            "total_agent_runs": snapshot.ai.total_agent_runs,
            "model_usage": snapshot.ai.model_usage,
            "input_tokens": snapshot.ai.input_tokens,
            "output_tokens": snapshot.ai.output_tokens,
            "cost_usd": snapshot.ai.cost_usd,
        },
        "execution": {
            "successful_actions": (
                snapshot.execution.successful_actions
            ),
            "failed_actions": (
                snapshot.execution.failed_actions
            ),
            "rollback_count": (
                snapshot.execution.rollback_count
            ),
        },
    }


@router.get(
    "/operations/metrics/incidents",
    summary="Get incident metrics",
)
def get_incident_metrics(
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    metrics = command_center.dashboard.incident_metrics()

    return {
        "total_incidents": metrics.total_incidents,
        "resolved_incidents": metrics.resolved_incidents,
        "open_incidents": metrics.open_incidents,
        "auto_resolution_rate": round(
            metrics.auto_resolution_rate,
            2,
        ),
        "average_resolution_time_s": round(
            metrics.average_resolution_time_s,
            2,
        ),
    }


@router.get(
    "/operations/metrics/ai",
    summary="Get AI metrics",
)
def get_ai_metrics(
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    metrics = command_center.dashboard.ai_metrics()

    return {
        "agent_success_rate": metrics.agent_success_rate,
        "total_agent_runs": metrics.total_agent_runs,
        "model_usage": metrics.model_usage,
        "input_tokens": metrics.input_tokens,
        "output_tokens": metrics.output_tokens,
        "cost_usd": metrics.cost_usd,
    }


@router.get(
    "/operations/metrics/execution",
    summary="Get execution metrics",
)
def get_execution_metrics(
    command_center: OperationsCommandCenter = Depends(
        get_operations_command_center,
    ),
):

    metrics = command_center.dashboard.execution_metrics()

    return {
        "successful_actions": metrics.successful_actions,
        "failed_actions": metrics.failed_actions,
        "rollback_count": metrics.rollback_count,
    }
