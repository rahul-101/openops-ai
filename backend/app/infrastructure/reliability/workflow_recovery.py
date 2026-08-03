from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from uuid import uuid4


class RecoveryStatus(str, Enum):
    """
    Lifecycle state of a workflow recovery.
    """

    PENDING = "pending"

    IN_PROGRESS = "in_progress"

    COMPLETED = "completed"

    FAILED = "failed"


@dataclass
class WorkflowStepState:
    """
    Captured state of a single workflow step.
    """

    step: str

    attempts: int = 0

    succeeded: bool = False

    failed: bool = False

    output: dict = field(default_factory=dict)

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class WorkflowCheckpoint:
    """
    A recoverable snapshot of a workflow execution.
    """

    workflow_id: str

    step: str

    state: dict = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class WorkflowRecoveryRecord:
    """
    A single workflow execution recovery record.
    """

    workflow_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    steps: dict[str, WorkflowStepState] = field(
        default_factory=dict
    )

    status: RecoveryStatus = RecoveryStatus.PENDING

    completed_steps: list[str] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class WorkflowRecovery:
    """
    Provides checkpointing, retry, resume and rollback for
    workflows.

    - Checkpointing: snapshot each completed step.
    - Retry: bounded retries for a failing step.
    - Resume: continue from the last completed checkpoint.
    - Rollback: mark a workflow for rollback and clear
      progress.
    """

    def __init__(
        self,
        max_retries: int = 2,
    ) -> None:

        self.max_retries = max_retries

        self._records: dict[str, WorkflowRecoveryRecord] = {}

        self._lock = Lock()

    def begin(
        self,
        workflow_id: str,
        steps: list[str],
    ) -> WorkflowRecoveryRecord:
        """
        Starts a recoverable workflow execution.
        """

        record = WorkflowRecoveryRecord(
            workflow_id=workflow_id,
            steps={
                step: WorkflowStepState(step=step)
                for step in steps
            },
            status=RecoveryStatus.IN_PROGRESS,
        )

        with self._lock:
            self._records[workflow_id] = record

        return record

    def checkpoint(
        self,
        workflow_id: str,
        step: str,
        output: dict | None = None,
    ) -> WorkflowCheckpoint:
        """
        Records a successfully completed step.
        """

        with self._lock:

            record = self._get_required(workflow_id)

            state = record.steps.get(step)

            if state is None:
                state = WorkflowStepState(step=step)
                record.steps[step] = state

            state.succeeded = True
            state.output = output or {}
            state.updated_at = datetime.utcnow()

            if step not in record.completed_steps:
                record.completed_steps.append(step)

            record.updated_at = datetime.utcnow()

            return WorkflowCheckpoint(
                workflow_id=workflow_id,
                step=step,
                state={
                    "completed_steps": list(
                        record.completed_steps
                    ),
                    "output": output or {},
                },
            )

    def record_failure(
        self,
        workflow_id: str,
        step: str,
    ) -> WorkflowStepState:
        """
        Records a step failure and increments retry count.
        """

        with self._lock:

            record = self._get_required(workflow_id)

            state = record.steps.get(step)

            if state is None:
                state = WorkflowStepState(step=step)
                record.steps[step] = state

            state.attempts += 1
            state.failed = True
            state.updated_at = datetime.utcnow()

            record.updated_at = datetime.utcnow()

            return state

    def can_retry(
        self,
        workflow_id: str,
        step: str,
    ) -> bool:
        """
        True when the step can be retried.

        `max_retries` bounds the number of retries after the
        initial attempt.
        """

        state = self.get_step(workflow_id, step)

        if state is None:
            return True

        return state.attempts <= self.max_retries

    def resume(
        self,
        workflow_id: str,
    ) -> list[str]:
        """
        Returns the steps to resume from the last checkpoint.
        """

        with self._lock:

            record = self._get_required(workflow_id)

            return [
                step
                for step in record.steps
                if not record.steps[step].succeeded
            ]

    def get_checkpoint(
        self,
        workflow_id: str,
    ) -> WorkflowCheckpoint | None:
        """
        Returns the last completed checkpoint.
        """

        with self._lock:

            record = self._records.get(workflow_id)

            if record is None or not record.completed_steps:
                return None

            last_step = record.completed_steps[-1]

            state = record.steps[last_step]

            return WorkflowCheckpoint(
                workflow_id=workflow_id,
                step=last_step,
                state={
                    "completed_steps": list(
                        record.completed_steps
                    ),
                    "output": dict(state.output),
                },
            )

    def complete(
        self,
        workflow_id: str,
    ) -> WorkflowRecoveryRecord:

        with self._lock:

            record = self._get_required(workflow_id)

            record.status = RecoveryStatus.COMPLETED
            record.updated_at = datetime.utcnow()

            return record

    def rollback(
        self,
        workflow_id: str,
    ) -> WorkflowRecoveryRecord:
        """
        Marks a workflow for rollback and clears progress.
        """

        with self._lock:

            record = self._records.get(workflow_id)

            if record is None:
                record = WorkflowRecoveryRecord(
                    workflow_id=workflow_id
                )
                self._records[workflow_id] = record

            record.status = RecoveryStatus.FAILED
            record.completed_steps.clear()

            for state in record.steps.values():
                state.succeeded = False

            record.updated_at = datetime.utcnow()

            return record

    def get(
        self,
        workflow_id: str,
    ) -> WorkflowRecoveryRecord | None:

        with self._lock:
            return self._records.get(workflow_id)

    def get_step(
        self,
        workflow_id: str,
        step: str,
    ) -> WorkflowStepState | None:

        with self._lock:

            record = self._records.get(workflow_id)

            if record is None:
                return None

            return record.steps.get(step)

    def list(self) -> list[WorkflowRecoveryRecord]:

        with self._lock:
            return list(self._records.values())

    def clear(self) -> None:

        with self._lock:
            self._records.clear()

    def _get_required(
        self,
        workflow_id: str,
    ) -> WorkflowRecoveryRecord:

        record = self._records.get(workflow_id)

        if record is None:
            raise KeyError(
                f"Workflow '{workflow_id}' not found."
            )

        return record
