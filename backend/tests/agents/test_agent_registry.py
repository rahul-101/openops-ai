import pytest

from app.application.agents.agent_registry import AgentRegistry
from tests.agents.fakes import FakeAgent


@pytest.fixture
def registry() -> AgentRegistry:

    registry = AgentRegistry()

    registry.register(
        FakeAgent(
            name="alpha",
            order=2,
        )
    )

    registry.register(
        FakeAgent(
            name="beta",
            order=1,
        )
    )

    return registry


def test_register_and_get(registry):

    assert registry.exists("alpha")
    assert registry.exists("beta")
    assert registry.get("alpha").name == "alpha"


def test_register_is_case_insensitive(registry):

    assert registry.get("ALPHA").name == "alpha"


def test_get_unknown_raises(registry):

    with pytest.raises(ValueError):
        registry.get("missing")


def test_list_sorted(registry):

    assert registry.list() == ["alpha", "beta"]


def test_ordered_by_metadata_order(registry):

    ordered = registry.ordered()

    assert [agent.name for agent in ordered] == [
        "beta",
        "alpha",
    ]


def test_len(registry):

    assert len(registry) == 2
