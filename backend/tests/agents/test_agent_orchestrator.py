import pytest

from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_registry import AgentRegistry
from app.application.agents.agent_result import AgentStatus
from app.application.orchestration.agent_orchestrator import (
    AgentOrchestrator,
)
from tests.agents.fakes import FakeAgent


class ExplodingAgent(FakeAgent):

    async def execute(self, context):
        raise RuntimeError("kaboom")


@pytest.fixture
def registry() -> AgentRegistry:

    registry = AgentRegistry()

    registry.register(
        FakeAgent(
            name="alpha",
            order=1,
        )
    )

    registry.register(
        FakeAgent(
            name="beta",
            order=2,
        )
    )

    return registry


@pytest.mark.asyncio
async def test_runs_agents_in_order_with_context_passing(registry):

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
    )

    results = await orchestrator.run(context)

    assert [result.agent for result in results] == [
        "alpha",
        "beta",
    ]

    assert context.get("alpha") == "done"
    assert context.get("beta") == "done"
    assert len(context.history) == 2


@pytest.mark.asyncio
async def test_honors_explicit_agent_order(registry):

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
    )

    results = await orchestrator.run(
        context,
        agent_names=["beta", "alpha"],
    )

    assert [result.agent for result in results] == [
        "beta",
        "alpha",
    ]


@pytest.mark.asyncio
async def test_stop_on_failure_halts_execution():

    registry = AgentRegistry()

    registry.register(
        FakeAgent(
            name="alpha",
            order=1,
            fail=True,
        )
    )

    registry.register(
        FakeAgent(
            name="beta",
            order=2,
        )
    )

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
    )

    results = await orchestrator.run(context)

    assert [result.agent for result in results] == [
        "alpha",
    ]

    assert results[0].status == AgentStatus.FAILURE


@pytest.mark.asyncio
async def test_continue_past_failure_when_disabled():

    registry = AgentRegistry()

    registry.register(
        FakeAgent(
            name="alpha",
            order=1,
            fail=True,
        )
    )

    registry.register(
        FakeAgent(
            name="beta",
            order=2,
        )
    )

    orchestrator = AgentOrchestrator(
        registry,
        stop_on_failure=False,
    )

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
    )

    results = await orchestrator.run(context)

    assert [result.agent for result in results] == [
        "alpha",
        "beta",
    ]


@pytest.mark.asyncio
async def test_exception_in_agent_returns_failure():

    registry = AgentRegistry()

    registry.register(
        ExplodingAgent(
            name="alpha",
            order=1,
        )
    )

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
    )

    results = await orchestrator.run(context)

    assert results[0].status == AgentStatus.FAILURE
    assert results[0].error == "kaboom"
