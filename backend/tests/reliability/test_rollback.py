from app.infrastructure.reliability.rollback import (
    RemediationRollback,
)


class FakeExecutor:
    """
    Records executed actions and returns success.
    """

    def __init__(self, success: bool = True) -> None:

        self.success = success
        self.calls: list[dict] = []

    def execute(
        self,
        tool_name: str,
        parameters: dict,
    ):

        self.calls.append(
            {
                "tool": tool_name,
                "parameters": parameters,
            }
        )

        class Result:
            success = self.success

        return Result()


def test_begin_and_snapshot():

    rollback = RemediationRollback()

    record = rollback.begin(incident_id="inc-1")

    change = rollback.snapshot(
        record.id,
        resource="deployment/payments",
        previous_state={"replicas": 3},
        rollback_actions=[
            {
                "tool": "kubernetes",
                "parameters": {"action": "scale"},
            }
        ],
    )

    assert change.resource == "deployment/payments"
    assert change.previous_state == {"replicas": 3}

    stored = rollback.get(record.id)

    assert len(stored.changes) == 1


def test_execute_rollback_runs_actions_reverse():

    rollback = RemediationRollback()

    executor = FakeExecutor()

    record = rollback.begin(incident_id="inc-1")

    rollback.snapshot(
        record.id,
        resource="service-a",
        previous_state={"state": "old-a"},
        rollback_actions=[
            {
                "tool": "kubernetes",
                "parameters": {"action": "restore", "id": "a"},
            }
        ],
    )

    rollback.snapshot(
        record.id,
        resource="service-b",
        previous_state={"state": "old-b"},
        rollback_actions=[
            {
                "tool": "kubernetes",
                "parameters": {"action": "restore", "id": "b"},
            }
        ],
    )

    result = rollback.execute_rollback(
        record.id,
        executor=executor,
    )

    assert result.rolled_back is True
    assert len(result.rollback_results) == 2

    # Reversed order: b first, then a
    assert result.rollback_results[0]["resource"] == "service-b"
    assert result.rollback_results[1]["resource"] == "service-a"


def test_execute_rollback_without_executor_records_only():

    rollback = RemediationRollback()

    record = rollback.begin(incident_id="inc-1")

    rollback.snapshot(
        record.id,
        resource="service-a",
        previous_state={},
        rollback_actions=[
            {
                "tool": "kubernetes",
                "parameters": {"action": "restore"},
            }
        ],
    )

    result = rollback.execute_rollback(record.id)

    assert result.rolled_back is True
    assert result.rollback_results[0]["success"] is True


def test_execute_rollback_is_idempotent():

    rollback = RemediationRollback()

    executor = FakeExecutor()

    record = rollback.begin(incident_id="inc-1")

    rollback.snapshot(
        record.id,
        resource="service-a",
        previous_state={},
        rollback_actions=[
            {
                "tool": "kubernetes",
                "parameters": {"action": "restore"},
            }
        ],
    )

    first = rollback.execute_rollback(record.id, executor=executor)
    second = rollback.execute_rollback(record.id, executor=executor)

    assert len(executor.calls) == 1
    assert second.rollback_results == first.rollback_results


def test_execute_rollback_failure_flag():

    rollback = RemediationRollback()

    executor = FakeExecutor(success=False)

    record = rollback.begin(incident_id="inc-1")

    rollback.snapshot(
        record.id,
        resource="service-a",
        previous_state={},
        rollback_actions=[
            {
                "tool": "kubernetes",
                "parameters": {"action": "restore"},
            }
        ],
    )

    result = rollback.execute_rollback(record.id, executor=executor)

    assert result.rolled_back is True
    assert result.rollback_results[0]["success"] is False


def test_list_by_incident():

    rollback = RemediationRollback()

    a = rollback.begin(incident_id="inc-1")
    _ = rollback.begin(incident_id="inc-2")

    records = rollback.list(incident_id="inc-1")

    assert [r.id for r in records] == [a.id]

    assert len(rollback.list()) == 2
