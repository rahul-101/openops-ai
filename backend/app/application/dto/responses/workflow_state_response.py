from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.incident_workflow_state import (
    WorkflowExecutionStatus,
)


class AgentHistoryResponse(BaseModel):
    """Response DTO for a single agent execution."""

    model_config = ConfigDict(from_attributes=True)

    agent: str

    status: str

    output: dict

    error: str | None = None

    duration_ms: float

    executed_at: datetime


class WorkflowStateResponse(BaseModel):
    """Response DTO for an incident workflow run."""

    incident_id: str

    workflow_id: str

    workflow_status: WorkflowExecutionStatus

    current_step: str | None = None

    agent_history: list[AgentHistoryResponse]

    recommendations: list[str]

    execution_result: dict | None = None

    created_at: datetime

    updated_at: datetime
