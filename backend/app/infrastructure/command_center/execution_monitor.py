from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from uuid import uuid4


class ExecutionStatus(str, Enum):
    """
    Lifecycle of a tracked agent execution.
    """

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"


@dataclass
class AgentExecution:
    """
    A single tracked agent execution.
    """

    agent: str

    execution_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    task: str = ""

    incident_id: str = ""

    status: ExecutionStatus = ExecutionStatus.RUNNING

    start_time: datetime = field(
        default_factory=datetime.utcnow
    )

    completion_time: datetime | None = None

    duration_ms: float = 0.0

    error: str | None = None

    def complete(
        self,
        success: bool,
        *,
        duration_ms: float | None = None,
        error: str | None = None,
    ) -> None:

        self.completion_time = datetime.utcnow()

        self.duration_ms = (
            duration_ms
            if duration_ms is not None
            else max(
                (self.completion_time - self.start_time).total_seconds() * 1000,
                0.0,
            )
        )

        self.status = (
            ExecutionStatus.COMPLETED
            if success
            else ExecutionStatus.FAILED
        )

        self.error = error

    def to_dict(self) -> dict:

        return {
            "execution_id": self.execution_id,
            "agent": self.agent,
            "task": self.task,
            "incident_id": self.incident_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "completion_time": (
                self.completion_time.isoformat()
                if self.completion_time
                else None
            ),
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


class ExecutionMonitor:
    """
    Thread safe tracker of agent executions: status, start
    time, completion time, duration and errors.
    """

    def __init__(self) -> None:

        self._executions: dict[str, AgentExecution] = {}

        self._lock = Lock()

    def start(
        self,
        agent: str,
        *,
        task: str = "",
        incident_id: str = "",
    ) -> AgentExecution:

        execution = AgentExecution(
            agent=agent,
            task=task,
            incident_id=incident_id,
        )

        with self._lock:
            self._executions[execution.execution_id] = execution

        return execution

    def complete(
        self,
        execution_id: str,
        success: bool,
        *,
        duration_ms: float | None = None,
        error: str | None = None,
    ) -> AgentExecution:

        with self._lock:

            execution = self._get_required(execution_id)

            execution.complete(
                success,
                duration_ms=duration_ms,
                error=error,
            )

            return execution

    def fail(
        self,
        execution_id: str,
        *,
        error: str | None = None,
    ) -> AgentExecution:

        return self.complete(
            execution_id,
            success=False,
            error=error,
        )

    def get(
        self,
        execution_id: str,
    ) -> AgentExecution | None:

        with self._lock:
            return self._executions.get(execution_id)

    def list(
        self,
        status: ExecutionStatus | None = None,
        incident_id: str | None = None,
    ) -> list[AgentExecution]:

        with self._lock:

            executions = [
                execution
                for execution in self._executions.values()
                if (
                    status is None
                    or execution.status == status
                )
                and (
                    incident_id is None
                    or execution.incident_id == incident_id
                )
            ]

            return list(executions)

    def summary(self) -> dict:

        with self._lock:

            executions = list(
                self._executions.values()
            )

        running = sum(
            1
            for execution in executions
            if execution.status == ExecutionStatus.RUNNING
        )

        completed = sum(
            1
            for execution in executions
            if execution.status == ExecutionStatus.COMPLETED
        )

        failed = sum(
            1
            for execution in executions
            if execution.status == ExecutionStatus.FAILED
        )

        return {
            "total": len(executions),
            "running": running,
            "completed": completed,
            "failed": failed,
            "success_rate": (
                (completed / (completed + failed)) * 100
                if (completed + failed)
                else 0.0
            ),
        }

    def clear(self) -> None:

        with self._lock:
            self._executions.clear()

    def _get_required(
        self,
        execution_id: str,
    ) -> AgentExecution:

        execution = self._executions.get(execution_id)

        if execution is None:
            raise KeyError(
                f"Execution '{execution_id}' not found."
            )

        return execution
