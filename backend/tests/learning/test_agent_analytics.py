from app.infrastructure.learning.agent_analytics import (
    AgentAnalytics,
)

import pytest


def test_register_agent():

    analytics = AgentAnalytics()

    analytics.register_agent("triage-agent")

    assert len(analytics.get_analytics()) == 1


def test_record_run_success_and_failure():

    analytics = AgentAnalytics()

    analytics.record_run(
        agent="triage-agent",
        success=True,
        latency_ms=300.0,
    )

    analytics.record_run(
        agent="triage-agent",
        success=False,
        latency_ms=700.0,
    )

    stats = analytics.get_agent("triage-agent")

    assert stats.total_runs == 2
    assert stats.successful_runs == 1
    assert stats.failed_runs == 1
    assert stats.success_rate == 50.0
    assert stats.average_latency_ms == 500.0


def test_get_agent_defaults():

    analytics = AgentAnalytics()

    stats = analytics.get_agent("ghost-agent")

    assert stats.total_runs == 0
    assert stats.success_rate == 100.0
    assert stats.average_latency_ms == 0.0


def test_get_analytics_filtered_by_agent():

    analytics = AgentAnalytics()

    analytics.record_run(
        agent="triage-agent",
        success=True,
    )

    analytics.record_run(
        agent="analysis-agent",
        success=True,
    )

    stats = analytics.get_analytics(agent="triage-agent")

    assert len(stats) == 1
    assert stats[0].agent == "triage-agent"


def test_get_summary_empty():

    analytics = AgentAnalytics()

    summary = analytics.get_summary()

    assert summary["total_agents"] == 0
    assert summary["total_runs"] == 0
    assert summary["overall_success_rate"] == 0.0


def test_get_summary_aggregates():

    analytics = AgentAnalytics()

    analytics.record_run(
        agent="triage-agent",
        success=True,
    )

    analytics.record_run(
        agent="triage-agent",
        success=False,
    )

    analytics.record_run(
        agent="analysis-agent",
        success=True,
    )

    summary = analytics.get_summary()

    assert summary["total_agents"] == 2
    assert summary["total_runs"] == 3
    assert summary["overall_success_rate"] == pytest.approx(
        (2 / 3) * 100
    )


def test_clear():

    analytics = AgentAnalytics()

    analytics.record_run(
        agent="triage-agent",
        success=True,
    )

    analytics.clear()

    assert analytics.get_analytics() == []
