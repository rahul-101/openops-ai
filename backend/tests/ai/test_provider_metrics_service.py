import pytest

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)


@pytest.fixture
def metrics_service() -> ProviderMetricsService:
    service = ProviderMetricsService()
    service.register_provider("gemini")
    return service


# ==========================================================
# Registration
# ==========================================================


def test_register_provider(
    metrics_service: ProviderMetricsService,
):

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert metrics.provider == "gemini"

    assert metrics.total_requests == 0

    assert metrics.successful_requests == 0

    assert metrics.failed_requests == 0


# ==========================================================
# Success
# ==========================================================


def test_mark_success(
    metrics_service: ProviderMetricsService,
):

    metrics_service.mark_success(
        provider_name="gemini",
        response_time_ms=100,
    )

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert metrics.total_requests == 1

    assert metrics.successful_requests == 1

    assert metrics.failed_requests == 0

    assert metrics.last_response_time_ms == 100

    assert metrics.average_response_time_ms == 100


# ==========================================================
# Failure
# ==========================================================


def test_mark_failure(
    metrics_service: ProviderMetricsService,
):

    metrics_service.mark_failure(
        provider_name="gemini",
        response_time_ms=250,
        error=Exception("Failure"),
    )

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert metrics.total_requests == 1

    assert metrics.failed_requests == 1

    assert metrics.successful_requests == 0

    assert metrics.last_response_time_ms == 250

    assert metrics.last_error == "Failure"


# ==========================================================
# Average Latency
# ==========================================================


def test_average_latency(
    metrics_service: ProviderMetricsService,
):

    metrics_service.mark_success(
        "gemini",
        100,
    )

    metrics_service.mark_success(
        "gemini",
        200,
    )

    metrics_service.mark_success(
        "gemini",
        300,
    )

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert metrics.average_response_time_ms == 200


# ==========================================================
# Success Rate
# ==========================================================


def test_success_rate(
    metrics_service: ProviderMetricsService,
):

    metrics_service.mark_success(
        "gemini",
        100,
    )

    metrics_service.mark_success(
        "gemini",
        120,
    )

    metrics_service.mark_failure(
        "gemini",
        150,
        Exception("Failure"),
    )

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert metrics.total_requests == 3

    assert metrics.successful_requests == 2

    assert metrics.failed_requests == 1

    assert metrics.success_rate == pytest.approx(
        66.67,
        abs=0.1,
    )


# ==========================================================
# Failure Rate
# ==========================================================


def test_failure_rate(
    metrics_service: ProviderMetricsService,
):

    metrics_service.mark_success(
        "gemini",
        100,
    )

    metrics_service.mark_failure(
        "gemini",
        150,
        Exception("Failure"),
    )

    metrics_service.mark_failure(
        "gemini",
        180,
        Exception("Failure"),
    )

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert metrics.failure_rate == pytest.approx(
        66.67,
        abs=0.1,
    )


# ==========================================================
# Last Error
# ==========================================================


def test_last_error(
    metrics_service: ProviderMetricsService,
):

    metrics_service.mark_failure(
        "gemini",
        100,
        Exception("Provider Timeout"),
    )

    metrics = metrics_service.get_metrics(
        "gemini",
    )

    assert (
        metrics.last_error
        == "Provider Timeout"
    )