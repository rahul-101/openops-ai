from app.infrastructure.learning.cost_optimizer import (
    CostOptimizer,
    ModelOption,
)

import pytest


def _model(
    *,
    provider: str,
    model: str,
    input_cost: float = 0.0,
    output_cost: float = 0.0,
    capabilities: frozenset[str] = frozenset(),
) -> ModelOption:

    return ModelOption(
        provider=provider,
        model=model,
        input_cost_per_1k_tokens=input_cost,
        output_cost_per_1k_tokens=output_cost,
        capabilities=capabilities,
    )


def test_register_model():

    optimizer = CostOptimizer()

    option = optimizer.register_model(
        provider="gemini",
        model="gemini-2.0-flash",
        input_cost_per_1k_tokens=0.000075,
        output_cost_per_1k_tokens=0.0003,
        capabilities=frozenset(
            {"text_generation", "structured_output"}
        ),
    )

    assert option.provider == "gemini"
    assert option.model == "gemini-2.0-flash"
    assert len(optimizer.list_models()) == 1


def test_choose_returns_cheapest():

    optimizer = CostOptimizer()

    optimizer.register_model(
        provider="gemini",
        model="flash",
        input_cost_per_1k_tokens=0.000075,
        output_cost_per_1k_tokens=0.0003,
    )

    optimizer.register_model(
        provider="openrouter",
        model="pro",
        input_cost_per_1k_tokens=0.01,
        output_cost_per_1k_tokens=0.03,
    )

    chosen = optimizer.choose(
        input_tokens=1000,
        output_tokens=1000,
    )

    assert chosen is not None
    assert chosen.model == "flash"


def test_choose_respects_capabilities():

    optimizer = CostOptimizer()

    optimizer.register_model(
        provider="gemini",
        model="flash",
        input_cost_per_1k_tokens=0.0,
        output_cost_per_1k_tokens=0.0,
        capabilities=frozenset({"text_generation"}),
    )

    optimizer.register_model(
        provider="openrouter",
        model="function-model",
        input_cost_per_1k_tokens=0.0,
        output_cost_per_1k_tokens=0.0,
        capabilities=frozenset(
            {"text_generation", "function_calling"}
        ),
    )

    chosen = optimizer.choose(
        required_capabilities=frozenset(
            {"function_calling"}
        )
    )

    assert chosen is not None
    assert chosen.model == "function-model"


def test_choose_respects_providers():

    optimizer = CostOptimizer()

    optimizer.register_model(
        provider="gemini",
        model="flash",
        input_cost_per_1k_tokens=0.0,
        output_cost_per_1k_tokens=0.0,
    )

    optimizer.register_model(
        provider="openrouter",
        model="pro",
        input_cost_per_1k_tokens=0.0,
        output_cost_per_1k_tokens=0.0,
    )

    chosen = optimizer.choose(
        providers=frozenset({"openrouter"})
    )

    assert chosen is not None
    assert chosen.provider == "openrouter"


def test_choose_none_when_no_capability_match():

    optimizer = CostOptimizer()

    optimizer.register_model(
        provider="gemini",
        model="flash",
        capabilities=frozenset({"text_generation"}),
    )

    chosen = optimizer.choose(
        required_capabilities=frozenset(
            {"streaming", "long_context"}
        )
    )

    assert chosen is None


def test_choose_none_when_no_models():

    optimizer = CostOptimizer()

    assert optimizer.choose() is None


def test_estimated_cost():

    option = _model(
        provider="gemini",
        model="flash",
        input_cost=0.000075,
        output_cost=0.0003,
    )

    cost = option.estimated_cost(
        input_tokens=2000,
        output_tokens=1000,
    )

    assert cost == pytest.approx(
        (2 * 0.000075) + (1 * 0.0003)
    )


def test_clear():

    optimizer = CostOptimizer()

    optimizer.register_model(
        provider="gemini",
        model="flash",
    )

    optimizer.clear()

    assert optimizer.list_models() == []
