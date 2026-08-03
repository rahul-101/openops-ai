from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from uuid import uuid4


@dataclass
class StateChange:
    """
    A stored previous state with rollback actions.
    """

    resource: str

    previous_state: dict = field(default_factory=dict)

    rollback_actions: list[dict] = field(
        default_factory=list
    )


@dataclass
class RollbackRecord:
    """
    A single remediation rollback record.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    incident_id: str = ""

    changes: list[StateChange] = field(
        default_factory=list
    )

    rolled_back: bool = False

    rollback_results: list[dict] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RemediationRollback:
    """
    Stores the previous state before remediation and executes
    rollback actions to restore it on failure.
    """

    def __init__(self) -> None:

        self._records: dict[str, RollbackRecord] = {}

        self._lock = Lock()

    def begin(
        self,
        incident_id: str,
    ) -> RollbackRecord:
        """
        Starts a rollback record for an incident.
        """

        record = RollbackRecord(
            incident_id=incident_id,
        )

        with self._lock:
            self._records[record.id] = record

        return record

    def snapshot(
        self,
        record_id: str,
        *,
        resource: str,
        previous_state: dict,
        rollback_actions: list[dict],
    ) -> StateChange:
        """
        Stores the previous state of a resource before a
        remediation action.
        """

        change = StateChange(
            resource=resource,
            previous_state=dict(previous_state),
            rollback_actions=[
                dict(action) for action in rollback_actions
            ],
        )

        with self._lock:

            record = self._get_required(record_id)

            record.changes.append(change)
            record.updated_at = datetime.utcnow()

            return change

    def execute_rollback(
        self,
        record_id: str,
        executor=None,
    ) -> RollbackRecord:
        """
        Executes the rollback actions in reverse order.
        """

        with self._lock:

            record = self._get_required(record_id)

            if record.rolled_back:
                return record

        results: list[dict] = []

        for change in reversed(record.changes):

            for action in reversed(change.rollback_actions):

                result = self._execute_action(
                    action,
                    executor,
                )

                results.append(
                    {
                        "resource": change.resource,
                        "action": action,
                        "success": result,
                    }
                )

        with self._lock:

            record.rollback_results = results
            record.rolled_back = True
            record.updated_at = datetime.utcnow()

            return record

    def get(
        self,
        record_id: str,
    ) -> RollbackRecord | None:

        with self._lock:
            return self._records.get(record_id)

    def list(
        self,
        incident_id: str | None = None,
    ) -> list[RollbackRecord]:

        with self._lock:

            records = [
                record
                for record in self._records.values()
                if (
                    incident_id is None
                    or record.incident_id == incident_id
                )
            ]

            return list(records)

    def clear(self) -> None:

        with self._lock:
            self._records.clear()

    @staticmethod
    def _execute_action(
        action: dict,
        executor,
    ) -> bool:
        """
        Executes a single rollback action. Returns True when
        the action succeeded or no executor is configured
        (recorded only).
        """

        if executor is None:
            return True

        try:

            tool = action.get("tool")

            if tool is None:
                return True

            parameters = action.get("parameters", {})

            result = executor.execute(
                tool_name=tool,
                parameters=parameters,
            )

            return result.success

        except Exception:

            return False

    def _get_required(
        self,
        record_id: str,
    ) -> RollbackRecord:

        record = self._records.get(record_id)

        if record is None:
            raise KeyError(
                f"Rollback record '{record_id}' not found."
            )

        return record
