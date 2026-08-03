import pytest

from app.infrastructure.reliability.chaos_simulator import (
    ChaosTestingSimulator,
    FailureType,
)


def test_inject_failure():

    simulator = ChaosTestingSimulator()

    experiment = simulator.inject_failure(
        name="restart-payments",
        target_service="payments",
        failure_type=FailureType.POD_RESTART,
        duration_seconds=120,
    )

    assert experiment.id
    assert experiment.name == "restart-payments"
    assert experiment.target_service == "payments"
    assert experiment.failure_type == FailureType.POD_RESTART
    assert experiment.duration_seconds == 120


def test_generate_alert():

    simulator = ChaosTestingSimulator()

    experiment = simulator.inject_failure(
        name="cpu-spike",
        target_service="checkout",
        failure_type=FailureType.CPU_SPIKE,
    )

    alert = simulator.generate_alert(experiment)

    assert alert["source"] == "chaos-simulator"
    assert alert["alert_id"] == experiment.id
    assert "cpu_spike" in alert["title"]
    assert alert["service"] == "checkout"
    assert alert["severity"] == "high"
    assert alert["metadata"]["chaos_experiment_id"] == experiment.id


def test_record_recovery():

    simulator = ChaosTestingSimulator()

    experiment = simulator.inject_failure(
        name="restart",
        target_service="payments",
        failure_type=FailureType.POD_RESTART,
    )

    updated = simulator.record_recovery(
        experiment.id,
        recovered=True,
        observation={"pod_healthy": True},
    )

    assert updated.recovered is True
    assert updated.recovery_validated is True
    assert updated.resolved is True
    assert updated.observation == {"pod_healthy": True}


def test_validate_recovery_false():

    simulator = ChaosTestingSimulator()

    experiment = simulator.inject_failure(
        name="restart",
        target_service="payments",
        failure_type=FailureType.POD_RESTART,
    )

    resolved = simulator.validate_recovery(
        experiment.id,
        resolved=False,
    )

    assert resolved is False

    stored = simulator.get(experiment.id)

    assert stored.recovery_validated is True
    assert stored.recovered is False


def test_recovery_rate():

    simulator = ChaosTestingSimulator()

    a = simulator.inject_failure(
        name="a",
        target_service="s1",
        failure_type=FailureType.SERVICE_DOWN,
    )

    b = simulator.inject_failure(
        name="b",
        target_service="s2",
        failure_type=FailureType.NETWORK_LATENCY,
    )

    simulator.record_recovery(a.id, recovered=True)
    simulator.record_recovery(b.id, recovered=False)

    assert simulator.get_recovery_rate() == 50.0


def test_recovery_rate_no_validated():

    simulator = ChaosTestingSimulator()

    simulator.inject_failure(
        name="a",
        target_service="s1",
        failure_type=FailureType.SERVICE_DOWN,
    )

    assert simulator.get_recovery_rate() == 0.0


def test_missing_experiment_raises():

    simulator = ChaosTestingSimulator()

    with pytest.raises(KeyError):
        simulator.validate_recovery("missing", True)


def test_clear():

    simulator = ChaosTestingSimulator()

    simulator.inject_failure(
        name="a",
        target_service="s1",
        failure_type=FailureType.SERVICE_DOWN,
    )

    simulator.clear()

    assert simulator.list() == []
