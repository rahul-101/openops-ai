from app.infrastructure.learning.prompt_optimizer import (
    PromptOptimizer,
)

import pytest


def test_register_prompt():

    optimizer = PromptOptimizer()

    optimizer.register_prompt("incident_analysis", "1.0.0")

    assert optimizer.get_best_version("incident_analysis") == "1.0.0"


def test_get_best_version_none_when_unregistered():

    optimizer = PromptOptimizer()

    assert optimizer.get_best_version("missing") is None


def test_record_evaluation_success_rate():

    optimizer = PromptOptimizer()

    optimizer.register_prompt("incident_analysis", "1.0.0")

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=True,
        latency_ms=500.0,
        tokens=100,
    )

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=True,
        latency_ms=500.0,
        tokens=100,
    )

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=False,
        latency_ms=500.0,
        tokens=100,
    )

    performance = optimizer.get_performance(
        "incident_analysis",
        "1.0.0",
    )

    assert performance.total_evaluations == 3
    assert performance.success_rate == pytest.approx(66.67, abs=0.01)


def test_record_evaluation_latency_and_tokens():

    optimizer = PromptOptimizer()

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=True,
        latency_ms=400.0,
        tokens=100,
    )

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=True,
        latency_ms=800.0,
        tokens=100,
    )

    performance = optimizer.get_performance(
        "incident_analysis",
        "1.0.0",
    )

    assert performance.average_latency_ms == 600.0
    assert performance.total_tokens == 200


def test_get_best_version_selects_highest_success():

    optimizer = PromptOptimizer()

    optimizer.register_prompt("incident_analysis", "1.0.0")
    optimizer.register_prompt("incident_analysis", "2.0.0")

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=True,
        latency_ms=500.0,
        tokens=100,
    )

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="1.0.0",
        success=True,
        latency_ms=500.0,
        tokens=100,
    )

    optimizer.record_evaluation(
        prompt_name="incident_analysis",
        version="2.0.0",
        success=False,
        latency_ms=500.0,
        tokens=100,
    )

    assert optimizer.get_best_version("incident_analysis") == "1.0.0"


def test_list_versions():

    optimizer = PromptOptimizer()

    optimizer.register_prompt("incident_analysis", "1.0.0")
    optimizer.register_prompt("incident_analysis", "2.0.0")

    versions = optimizer.list_versions("incident_analysis")

    assert len(versions) == 2


def test_clear():

    optimizer = PromptOptimizer()

    optimizer.register_prompt("incident_analysis", "1.0.0")

    optimizer.clear()

    assert optimizer.get_best_version("incident_analysis") is None
