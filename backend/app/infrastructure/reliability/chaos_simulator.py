from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from uuid import uuid4


class FailureType(str, Enum):
    """
    Type of failure injected by the chaos simulator.
    """

    POD_RESTART = "pod_restart"

    CPU_SPIKE = "cpu_spike"

    MEMORY_PRESSURE = "memory_pressure"

    NETWORK_LATENCY = "network_latency"

    SERVICE_DOWN = "service_down"

    DATABASE_TIMEOUT = "database_timeout"


@dataclass
class ChaosExperiment:
    """
    A single chaos failure injection.
    """

    name: str

    target_service: str

    failure_type: FailureType

    duration_seconds: int = 60

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    injected_at: datetime = field(
        default_factory=datetime.utcnow
    )

    resolved: bool = False

    recovered: bool = False

    recovery_validated: bool = False

    observation: dict = field(default_factory=dict)


class ChaosTestingSimulator:
    """
    Generates failures and validates autonomous recovery.

    - Injects simulated failures targeting services.
    - Generates alert events from injected failures.
    - Records whether autonomous recovery resolved the
      failure within the experiment duration.
    """

    def __init__(self) -> None:

        self._experiments: dict[str, ChaosExperiment] = {}

        self._lock = Lock()

    def inject_failure(
        self,
        *,
        name: str,
        target_service: str,
        failure_type: FailureType,
        duration_seconds: int = 60,
    ) -> ChaosExperiment:

        experiment = ChaosExperiment(
            name=name,
            target_service=target_service,
            failure_type=failure_type,
            duration_seconds=duration_seconds,
        )

        with self._lock:
            self._experiments[experiment.id] = experiment

        return experiment

    def generate_alert(
        self,
        experiment: ChaosExperiment,
    ) -> dict:
        """
        Produces an alert describing the injected failure.
        """

        return {
            "source": "chaos-simulator",
            "alert_id": experiment.id,
            "title": (
                f"{experiment.failure_type.value} on "
                f"{experiment.target_service}"
            ),
            "description": (
                f"Injected {experiment.failure_type.value} "
                f"into {experiment.target_service}."
            ),
            "severity": "high",
            "service": experiment.target_service,
            "tags": [experiment.failure_type.value],
            "metadata": {
                "chaos_experiment_id": experiment.id,
                "duration_seconds": (
                    experiment.duration_seconds
                ),
            },
        }

    def record_recovery(
        self,
        experiment_id: str,
        *,
        recovered: bool,
        observation: dict | None = None,
    ) -> ChaosExperiment:
        """
        Records the autonomous recovery outcome.
        """

        with self._lock:

            experiment = self._get_required(experiment_id)

            experiment.recovered = recovered
            experiment.recovery_validated = True
            experiment.resolved = recovered
            experiment.observation = observation or {}

            return experiment

    def validate_recovery(
        self,
        experiment_id: str,
        resolved: bool,
    ) -> bool:
        """
        Validates recovery by checking the failure resolved.
        """

        with self._lock:

            experiment = self._get_required(experiment_id)

            experiment.resolved = resolved

            if resolved:
                experiment.recovered = True

            experiment.recovery_validated = True

            return resolved

    def get(
        self,
        experiment_id: str,
    ) -> ChaosExperiment | None:

        with self._lock:
            return self._experiments.get(experiment_id)

    def list(self) -> list[ChaosExperiment]:

        with self._lock:
            return list(self._experiments.values())

    def get_recovery_rate(self) -> float:
        """
        Returns the percentage of validated experiments that
        recovered.
        """

        with self._lock:

            validated = [
                experiment
                for experiment in self._experiments.values()
                if experiment.recovery_validated
            ]

            if not validated:
                return 0.0

            recovered = sum(
                1
                for experiment in validated
                if experiment.recovered
            )

            return (recovered / len(validated)) * 100

    def clear(self) -> None:

        with self._lock:
            self._experiments.clear()

    def _get_required(
        self,
        experiment_id: str,
    ) -> ChaosExperiment:

        experiment = self._experiments.get(experiment_id)

        if experiment is None:
            raise KeyError(
                f"Chaos experiment '{experiment_id}' not found."
            )

        return experiment
