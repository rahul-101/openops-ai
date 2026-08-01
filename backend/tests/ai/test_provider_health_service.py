from datetime import timedelta

import pytest

from app.infrastructure.ai.health.circuit_state import (
    CircuitState,
)
from app.infrastructure.ai.health.provider_health import (
    ProviderStatus,
)
from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)


@pytest.fixture
def health_service() -> ProviderHealthService:
    service = ProviderHealthService()
    service.register_provider("gemini")
    return service


# ==========================================================
# Registration
# ==========================================================


def test_register_provider(
    health_service: ProviderHealthService,
):

    health = health_service.get_health("gemini")

    assert health.provider == "gemini"

    assert health.status == ProviderStatus.HEALTHY

    assert (
        health.circuit_state
        == CircuitState.CLOSED
    )


# ==========================================================
# Success
# ==========================================================


def test_mark_success_resets_failures(
    health_service: ProviderHealthService,
):

    health_service.mark_success("gemini")

    health = health_service.get_health("gemini")

    assert health.consecutive_failures == 0

    assert health.consecutive_successes == 1

    assert (
        health.circuit_state
        == CircuitState.CLOSED
    )

    assert health.status == ProviderStatus.HEALTHY


# ==========================================================
# Failure
# ==========================================================


def test_failure_counter(
    health_service: ProviderHealthService,
):

    health_service.mark_failure(
        "gemini",
        Exception("Failure"),
    )

    health = health_service.get_health("gemini")

    assert health.consecutive_failures == 1

    assert (
        health.circuit_state
        == CircuitState.CLOSED
    )


# ==========================================================
# Circuit Opens
# ==========================================================


def test_circuit_opens_after_threshold(
    health_service: ProviderHealthService,
):

    for _ in range(
        health_service.FAILURE_THRESHOLD
    ):

        health_service.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    health = health_service.get_health("gemini")

    assert (
        health.circuit_state
        == CircuitState.OPEN
    )

    assert health.status == ProviderStatus.UNHEALTHY

    assert health.retry_after is not None


# ==========================================================
# Open Circuit
# ==========================================================


def test_open_circuit_is_unhealthy(
    health_service: ProviderHealthService,
):

    for _ in range(
        health_service.FAILURE_THRESHOLD
    ):

        health_service.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    assert (
        health_service.is_healthy(
            "gemini",
        )
        is False
    )


# ==========================================================
# Half Open
# ==========================================================


def test_half_open_after_cooldown(
    health_service: ProviderHealthService,
):

    for _ in range(
        health_service.FAILURE_THRESHOLD
    ):

        health_service.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    health = health_service.get_health("gemini")

    health.retry_after -= timedelta(
        seconds=61
    )

    assert (
        health_service.is_healthy(
            "gemini",
        )
        is True
    )

    assert (
        health.circuit_state
        == CircuitState.HALF_OPEN
    )


# ==========================================================
# Half Open Success
# ==========================================================


def test_half_open_success_closes_circuit(
    health_service: ProviderHealthService,
):

    for _ in range(
        health_service.FAILURE_THRESHOLD
    ):

        health_service.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    health = health_service.get_health("gemini")

    health.retry_after -= timedelta(
        seconds=61
    )

    health_service.is_healthy("gemini")

    health_service.mark_success("gemini")

    assert (
        health.circuit_state
        == CircuitState.CLOSED
    )

    assert health.status == ProviderStatus.HEALTHY


# ==========================================================
# Half Open Failure
# ==========================================================


def test_half_open_failure_reopens_circuit(
    health_service: ProviderHealthService,
):

    for _ in range(
        health_service.FAILURE_THRESHOLD
    ):

        health_service.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    health = health_service.get_health("gemini")

    health.retry_after -= timedelta(
        seconds=61
    )

    health_service.is_healthy("gemini")

    health_service.mark_failure(
        "gemini",
        Exception("Failure"),
    )

    assert (
        health.circuit_state
        == CircuitState.OPEN
    )