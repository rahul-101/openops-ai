from app.infrastructure.reliability.root_cause_graph import (
    RootCauseGraph,
)


def test_add_factor_and_rank():

    graph = RootCauseGraph()

    graph.add_factor(
        "inc-1",
        factor="Database CPU exhaustion",
        service="database",
        weight=0.9,
        evidence="CPU at 99%",
    )

    graph.add_factor(
        "inc-1",
        factor="Connection pool depletion",
        service="api-gateway",
        weight=0.6,
        evidence="Too many connections",
    )

    graph.add_factor(
        "inc-1",
        factor="Deploy regression",
        service="checkout",
        weight=0.4,
        evidence="New release v2.3",
    )

    ranked = graph.rank_root_causes("inc-1")

    assert [f.weight for f in ranked] == [0.9, 0.6, 0.4]
    assert ranked[0].factor == "Database CPU exhaustion"


def test_add_dependency():

    graph = RootCauseGraph()

    graph.create("inc-1")

    graph.add_dependency("inc-1", "checkout", "database")
    graph.add_dependency("inc-1", "api-gateway", "checkout")

    edges = graph.get_edges("inc-1")

    assert ("checkout", "database") in edges
    assert ("api-gateway", "checkout") in edges


def test_get_nodes():

    graph = RootCauseGraph()

    graph.add_factor(
        "inc-1",
        factor="CPU",
        service="database",
        weight=0.9,
        evidence="x",
    )

    nodes = graph.get_nodes("inc-1")

    assert len(nodes) == 1
    assert nodes[0].name == "database"
    assert nodes[0].weight == 0.9


def test_rank_empty_returns_empty():

    graph = RootCauseGraph()

    assert graph.rank_root_causes("missing") == []
    assert graph.get_edges("missing") == []
    assert graph.get_nodes("missing") == []


def test_get_missing_returns_none():

    graph = RootCauseGraph()

    assert graph.get("missing") is None


def test_clear():

    graph = RootCauseGraph()

    graph.add_factor(
        "inc-1",
        factor="CPU",
        service="database",
    )

    graph.clear()

    assert graph.list() == []
