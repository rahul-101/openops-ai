from app.infrastructure.reasoning.model_selection import (
    DynamicModelSelector,
    TaskComplexity,
)


def build_selector() -> DynamicModelSelector:

    selector = DynamicModelSelector()

    selector.register_simple_model(
        name="gemini-flash",
        model="gemini-2.0-flash",
        provider="gemini",
        input_cost_per_1k_tokens=0.000075,
        output_cost_per_1k_tokens=0.0003,
    )

    selector.register_complex_model(
        name="gemini-pro",
        model="gemini-2.5-pro",
        provider="gemini",
        input_cost_per_1k_tokens=0.00125,
        output_cost_per_1k_tokens=0.005,
    )

    return selector


def test_simple_task_selects_cheaper_model():

    selector = build_selector()

    selection = selector.select(
        "lorem ipsum trivial notice",
        severity="low",
    )

    assert selection is not None
    assert selection.model == "gemini-2.0-flash"
    assert selection.complexity == TaskComplexity.SIMPLE
    assert "cheaper" in selection.reason


def test_complex_task_selects_stronger_model():

    selector = build_selector()

    selection = selector.select(
        "cross-service database timeout requires root cause "
        "analysis with rollback",
        severity="high",
    )

    assert selection is not None
    assert selection.model == "gemini-2.5-pro"
    assert selection.complexity == TaskComplexity.COMPLEX


def test_classify_simple():

    selector = build_selector()

    complexity = selector.classify(
        "log rotation finished",
        severity="low",
    )

    assert complexity == TaskComplexity.SIMPLE


def test_classify_complex():

    selector = build_selector()

    complexity = selector.classify(
        "distributed transaction timeout "
        "root cause recovery",
        severity="high",
        tags=["database", "network"],
    )

    assert complexity == TaskComplexity.COMPLEX


def test_classify_moderate_high_severity():

    selector = build_selector()

    complexity = selector.classify(
        "unrelated log message",
        severity="high",
    )

    assert complexity == TaskComplexity.MODERATE


def test_select_no_models_returns_none():

    selector = DynamicModelSelector()

    assert selector.select("anything") is None


def test_list_models():

    selector = build_selector()

    models = selector.list_models()

    assert "gemini-2.0-flash" in models["simple"]
    assert "gemini-2.5-pro" in models["complex"]
