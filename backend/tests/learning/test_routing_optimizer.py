from app.infrastructure.learning.routing_optimizer import (
    RoutingOptimizer,
)


def test_register_provider():

    optimizer = RoutingOptimizer()

    optimizer.register_provider("gemini")
    optimizer.register_provider("openrouter")

    assert len(optimizer.get_all_performance()) == 2


def test_record_outcome_success_and_failure():

    optimizer = RoutingOptimizer()

    optimizer.record_outcome(
        provider="gemini",
        success=True,
        latency_ms=500.0,
    )

    optimizer.record_outcome(
        provider="gemini",
        success=False,
        latency_ms=900.0,
    )

    performance = optimizer.get_performance("gemini")

    assert performance.total_calls == 2
    assert performance.successful_calls == 1
    assert performance.failed_calls == 1
    assert performance.success_rate == 50.0
    assert performance.average_latency_ms == 700.0


def test_get_performance_defaults():

    optimizer = RoutingOptimizer()

    performance = optimizer.get_performance("unknown")

    assert performance.total_calls == 0
    assert performance.success_rate == 100.0
    assert performance.average_latency_ms == 0.0


def test_rank_providers_puts_successful_first():

    optimizer = RoutingOptimizer()

    optimizer.record_outcome(
        provider="gemini",
        success=True,
        latency_ms=500.0,
    )

    optimizer.record_outcome(
        provider="openrouter",
        success=False,
        latency_ms=900.0,
    )

    ranked = optimizer.rank_providers()

    assert ranked[0] == "gemini"
    assert ranked[1] == "openrouter"


def test_rank_prefers_lower_latency():

    optimizer = RoutingOptimizer()

    optimizer.record_outcome(
        provider="gemini",
        success=True,
        latency_ms=2000.0,
    )

    optimizer.record_outcome(
        provider="openrouter",
        success=True,
        latency_ms=100.0,
    )

    ranked = optimizer.rank_providers()

    assert ranked[0] == "openrouter"


def test_clear():

    optimizer = RoutingOptimizer()

    optimizer.record_outcome(
        provider="gemini",
        success=True,
    )

    optimizer.clear()

    assert optimizer.get_all_performance() == []
