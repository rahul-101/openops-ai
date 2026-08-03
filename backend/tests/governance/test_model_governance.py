from app.infrastructure.governance.model_governance import (
    ModelGovernanceService,
)


def test_record_usage():

    service = ModelGovernanceService()

    record = service.record_usage(
        provider="openai",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.002,
        latency_ms=450.0,
        action="incident.analyze",
    )

    assert record.provider == "openai"
    assert record.model == "gpt-4o"
    assert record.input_tokens == 100
    assert record.output_tokens == 50
    assert record.cost_usd == 0.002
    assert record.latency_ms == 450.0
    assert record.action == "incident.analyze"


def test_list_all_records():

    service = ModelGovernanceService()

    service.record_usage(
        provider="openai",
        model="gpt-4o",
    )

    service.record_usage(
        provider="anthropic",
        model="claude-3",
    )

    assert len(service.list()) == 2


def test_list_filter_by_provider():

    service = ModelGovernanceService()

    service.record_usage(
        provider="openai",
        model="gpt-4o",
    )

    service.record_usage(
        provider="anthropic",
        model="claude-3",
    )

    records = service.list(provider="openai")

    assert len(records) == 1
    assert records[0].provider == "openai"


def test_get_stats_empty():

    service = ModelGovernanceService()

    stats = service.get_stats()

    assert stats["total_requests"] == 0
    assert stats["total_cost_usd"] == 0.0


def test_get_stats_aggregates():

    service = ModelGovernanceService()

    service.record_usage(
        provider="openai",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.002,
        latency_ms=400.0,
    )

    service.record_usage(
        provider="openai",
        model="gpt-4o",
        input_tokens=200,
        output_tokens=100,
        cost_usd=0.004,
        latency_ms=600.0,
    )

    stats = service.get_stats(provider="openai")

    assert stats["total_requests"] == 2
    assert stats["total_tokens"] == 450
    assert round(stats["total_cost_usd"], 6) == 0.006
    assert stats["average_latency_ms"] == 500.0
    assert stats["providers"]["openai"]["requests"] == 2


def test_clear():

    service = ModelGovernanceService()

    service.record_usage(
        provider="openai",
        model="gpt-4o",
    )

    service.clear()

    assert service.list() == []
