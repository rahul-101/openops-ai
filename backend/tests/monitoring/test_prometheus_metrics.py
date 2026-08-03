from app.infrastructure.ai.health.circuit_state import (
    CircuitState,
)
from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)
from app.infrastructure.monitoring.metrics_registry import (
    MetricsRegistry,
)


def test_record_success_updates_counters():

    registry = MetricsRegistry()

    registry.record_success(
        provider="gemini",
        latency_s=0.5,
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.01,
    )

    output = registry.render().decode()

    assert "ai_requests_total" in output
    assert "ai_provider_successes_total" in output
    assert "ai_provider_input_tokens_total" in output
    assert "ai_provider_output_tokens_total" in output
    assert "ai_provider_cost_usd_total" in output


def test_record_failure_updates_failure_counter():

    registry = MetricsRegistry()

    registry.record_failure(
        provider="gemini",
        latency_s=1.0,
    )

    output = registry.render().decode()

    assert "ai_provider_failures_total" in output
    assert "ai_provider_latency_seconds" in output


def test_sync_provider_health_sets_circuit_state():

    health = ProviderHealthService()

    health.register_provider("gemini")

    registry = MetricsRegistry()

    registry.sync_provider_health(health)

    output = registry.render().decode()

    assert "ai_provider_circuit_state" in output
    assert 'ai_provider_circuit_state{provider="gemini"} 0.0' in output


def test_circuit_state_value_mapping():

    registry = MetricsRegistry()

    registry.update_circuit_state(
        "gemini",
        CircuitState.OPEN,
    )

    output = registry.render().decode()

    assert 'ai_provider_circuit_state{provider="gemini"} 2.0' in output
