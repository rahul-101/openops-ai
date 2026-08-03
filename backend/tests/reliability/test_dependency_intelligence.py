from app.infrastructure.reliability.dependency_intelligence import (
    DependencyIntelligence,
)


def build_intelligence() -> DependencyIntelligence:

    intelligence = DependencyIntelligence()

    intelligence.register_dependency(
        dependent="api-gateway",
        dependency="checkout",
    )

    intelligence.register_dependency(
        dependent="checkout",
        dependency="database",
        critical=True,
    )

    intelligence.register_dependency(
        dependent="recommendations",
        dependency="database",
    )

    return intelligence


def test_dependencies_of():

    intelligence = build_intelligence()

    deps = intelligence.dependencies_of("api-gateway")

    assert [d.dependency for d in deps] == ["checkout"]


def test_dependents_of():

    intelligence = build_intelligence()

    deps = intelligence.dependents_of("database")

    assert sorted(d.dependent for d in deps) == [
        "checkout",
        "recommendations",
    ]


def test_impact_analysis_direct_affected():

    intelligence = build_intelligence()

    impact = intelligence.impact_analysis("database")

    assert impact.directly_affected == [
        "checkout",
        "recommendations",
    ]

    assert "checkout" in impact.critical_dependencies


def test_impact_analysis_transitive():

    intelligence = build_intelligence()

    impact = intelligence.impact_analysis("database")

    assert "api-gateway" in impact.transitively_affected
    assert "recommendations" in impact.directly_affected


def test_is_affected():

    intelligence = build_intelligence()

    assert intelligence.is_affected("api-gateway", "database") is True
    assert intelligence.is_affected("database", "api-gateway") is False


def test_transitive_chain():

    intelligence = DependencyIntelligence()

    intelligence.register_dependency(
        dependent="web",
        dependency="api",
    )

    intelligence.register_dependency(
        dependent="api",
        dependency="db",
    )

    impact = intelligence.impact_analysis("db")

    assert impact.directly_affected == ["api"]
    assert impact.transitively_affected == ["web"]


def test_clear():

    intelligence = build_intelligence()

    intelligence.clear()

    assert intelligence.list() == []
