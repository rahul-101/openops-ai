from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class WorkflowExecutionStatus(str, Enum):
    """
    Execution status of an incident workflow.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    PARTIALLY_COMPLETED = "partially_completed"


@dataclass
class AgentHistoryEntry:
    """
    Immutable record of one agent execution.
    """

    agent: str

    status: str

    output: dict = field(default_factory=dict)

    error: str | None = None

    duration_ms: float = 0.0

    executed_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class IncidentWorkflowState:
    """
    Tracks the full state of an incident workflow run.

    Used for observability, resumability and result
    reporting.
    """

    incident_id: str

    workflow_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    workflow_status: WorkflowExecutionStatus = (
        WorkflowExecutionStatus.PENDING
    )

    current_step: str | None = None

    agent_history: list[AgentHistoryEntry] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )

    execution_result: dict | None = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def add_history(
        self,
        entry: AgentHistoryEntry,
    ) -> None:
        self.agent_history.append(entry)
        self.touch()
