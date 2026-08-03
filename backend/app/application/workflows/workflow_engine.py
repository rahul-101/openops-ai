from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)
from app.application.orchestration.agent_orchestrator import (
    AgentOrchestrator,
)


class WorkflowStatus(str, Enum):
    """
    Lifecycle state of a workflow.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    PARTIALLY_COMPLETED = "partially_completed"


class WorkflowStepStatus(str, Enum):
    """
    Execution state of a single workflow step (agent).
    """

    PENDING = "pending"

    IN_PROGRESS = "in_progress"

    SUCCEEDED = "succeeded"

    FAILED = "failed"

    SKIPPED = "skipped"


@dataclass
class WorkflowCheckpoint:
    """
    Snapshot of workflow progress used for resumability.
    """

    step_name: str

    status: WorkflowStatus

    state_snapshot: dict = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class WorkflowEngine:
    """
    Executes an agent sequence with lifecycle management.

    Supports:
    - Workflow lifecycle + execution states
    - Retries (transient agent failures)
    - Checkpoints (resume from last successful step)
    - Failure handling (fail-fast vs partial completion)
    """

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        max_retries: int = 2,
        stop_on_failure: bool = True,
    ) -> None:

        self.orchestrator = orchestrator
        self.max_retries = max_retries
        self.stop_on_failure = stop_on_failure

        self._status = WorkflowStatus.PENDING
        self._current_step: str | None = None
        self._step_status: dict[str, WorkflowStepStatus] = {}
        self._succeeded: set[str] = set()
        self._checkpoints: list[WorkflowCheckpoint] = []

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def status(self) -> WorkflowStatus:
        return self._status

    @property
    def current_step(self) -> str | None:
        return self._current_step

    def step_status(
        self,
        name: str,
    ) -> WorkflowStepStatus:
        return self._step_status.get(
            name,
            WorkflowStepStatus.PENDING,
        )

    def get_checkpoints(self) -> list[WorkflowCheckpoint]:
        return list(self._checkpoints)

    # ==========================================================
    # Execution
    # ==========================================================

    async def execute(
        self,
        context: AgentContext,
        agent_names: list[str] | None = None,
    ) -> list[AgentResult]:

        self._reset()

        self._status = WorkflowStatus.RUNNING

        final_failures: list[AgentResult] = []

        for attempt in range(self.max_retries + 1):

            remaining = self._remaining_agents(
                agent_names
            )

            if not remaining:
                break

            history = await self.orchestrator.run(
                context,
                remaining,
            )

            self._record_results(history)

            attempt_failures = [
                result
                for result in history
                if result.status == AgentStatus.FAILURE
            ]

            self._checkpoint(
                step_name=f"attempt_{attempt + 1}",
                status=self._attempt_status(
                    attempt,
                    attempt_failures,
                ),
                history=history,
            )

            final_failures = attempt_failures

            if not final_failures:
                break

        self._finalize(final_failures)

        return self._final_results(
            agent_names,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _reset(self) -> None:

        self._status = WorkflowStatus.PENDING
        self._current_step = None
        self._step_status = {}
        self._succeeded = set()
        self._results: dict[str, AgentResult] = {}
        self._checkpoints = []

    def _remaining_agents(
        self,
        agent_names: list[str] | None,
    ) -> list[str]:

        names = agent_names or [
            agent.name
            for agent in self.orchestrator.registry.ordered()
        ]

        return [
            name
            for name in names
            if name.lower() not in self._succeeded
        ]

    def _record_results(
        self,
        history: list[AgentResult],
    ) -> None:

        for result in history:

            self._current_step = result.agent

            self._results[result.agent] = result

            if result.status == AgentStatus.SUCCESS:

                self._step_status[result.agent] = (
                    WorkflowStepStatus.SUCCEEDED
                )

                self._succeeded.add(
                    result.agent.lower()
                )

            elif result.status == AgentStatus.FAILURE:

                self._step_status[result.agent] = (
                    WorkflowStepStatus.FAILED
                )

    def _checkpoint(
        self,
        step_name: str,
        status: WorkflowStatus,
        history: list[AgentResult],
    ) -> None:

        self._checkpoints.append(
            WorkflowCheckpoint(
                step_name=step_name,
                status=status,
                state_snapshot={
                    result.agent: result.status.value
                    for result in history
                },
            )
        )

    def _attempt_status(
        self,
        attempt: int,
        failures: list[AgentResult],
    ) -> WorkflowStatus:

        if not failures:
            return WorkflowStatus.COMPLETED

        if attempt < self.max_retries:
            return WorkflowStatus.RUNNING

        if self.stop_on_failure:
            return WorkflowStatus.FAILED

        return WorkflowStatus.PARTIALLY_COMPLETED

    def _final_results(
        self,
        agent_names: list[str] | None,
    ) -> list[AgentResult]:

        names = agent_names or [
            agent.name
            for agent in self.orchestrator.registry.ordered()
        ]

        return [
            self._results[name]
            for name in names
            if name in self._results
        ]

    def _finalize(
        self,
        final_failures: list[AgentResult],
    ) -> None:

        if not final_failures:

            self._status = WorkflowStatus.COMPLETED

        elif self.stop_on_failure:

            self._status = WorkflowStatus.FAILED

        else:

            self._status = (
                WorkflowStatus.PARTIALLY_COMPLETED
            )
