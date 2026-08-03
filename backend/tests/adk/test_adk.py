import pytest

from app.infrastructure.adk.adk_agent import AdkAgent
from app.infrastructure.adk.adk_orchestrator import (
    AdkOrchestrator,
)
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)


class FakeRunner:
    """In-memory ADK runner stand-in for tests."""

    def __init__(
        self,
        agent,
        chunks: list[str] | None = None,
    ) -> None:
        self.agent = agent
        self.chunks = chunks or ["response text"]

    async def run_async(self, **kwargs):
        from google.adk.events import Event
        from google.genai import types

        for chunk in self.chunks:
            yield Event(
                author="agent",
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=chunk)],
                ),
                invocation_id="test-invocation",
            )


class FakeAdkAgent:

    def __init__(
        self,
        name: str = "fake",
        **kwargs,
    ) -> None:
        self.name = name


class TestAdkAgent:

    def test_constructs_with_metadata(self):

        agent = AdkAgent(
            name="investigator",
            instruction="Analyse the incident.",
            description="ADK investigator",
            order=5,
        )

        assert agent.name == "investigator"

        assert agent.metadata.description == "ADK investigator"

        assert agent.metadata.order == 5

    @pytest.mark.asyncio
    async def test_execute_with_runner_factory(
        self,
    ):

        runner = FakeRunner(None)

        agent = AdkAgent(
            name="investigator",
            instruction="Analyse the incident.",
            runner_factory=lambda adk_agent: runner,
        )

        context = AgentContext(
            incident_id="INC-1",
            workflow_id="WF-1",
            input={"title": "DB down"},
        )

        result = await agent.execute(context)

        assert isinstance(result, AgentResult)
        assert result.status == AgentStatus.SUCCESS

        assert result.output["text"] == "response text"

        assert context.get("investigator") == result.output

    @pytest.mark.asyncio
    async def test_execute_joins_multiple_chunks(
        self,
    ):

        runner = FakeRunner(
            None,
            chunks=["part one", "part two"],
        )

        agent = AdkAgent(
            name="investigator",
            runner_factory=lambda adk_agent: runner,
        )

        context = AgentContext(
            incident_id="INC-2",
            workflow_id="WF-2",
        )

        result = await agent.execute(context)

        assert result.output["text"] == "part one\npart two"

    @pytest.mark.asyncio
    async def test_execute_adds_recommendation(
        self,
    ):

        runner = FakeRunner(None, chunks=["Do a rollback"])

        agent = AdkAgent(
            name="investigator",
            runner_factory=lambda adk_agent: runner,
        )

        context = AgentContext(
            incident_id="INC-3",
            workflow_id="WF-3",
        )

        await agent.execute(context)

        assert context.recommendations == ["Do a rollback"]

    @pytest.mark.asyncio
    async def test_existing_state_included_in_prompt(
        self,
    ):

        captured = {}

        class CapturingRunner(FakeRunner):

            async def run_async(self, **kwargs):
                captured["message"] = kwargs.get("new_message")
                async for event in super().run_async(**kwargs):
                    yield event

        runner = CapturingRunner(None)

        agent = AdkAgent(
            name="investigator",
            runner_factory=lambda adk_agent: runner,
        )

        context = AgentContext(
            incident_id="INC-4",
            workflow_id="WF-4",
            input={"title": "API error"},
        )

        context.set("prior", "context value")

        await agent.execute(context)

        message_text = captured["message"].parts[0].text

        assert "INC-4" in message_text

        assert "title: API error" in message_text

        assert "context value" in message_text


class TestAdkOrchestrator:

    @pytest.mark.asyncio
    async def test_runs_agents_in_order(
        self,
    ):

        agent_a = AdkAgent(
            name="first",
            runner_factory=lambda _: FakeRunner(None, chunks=["a"]),
        )

        agent_b = AdkAgent(
            name="second",
            runner_factory=lambda _: FakeRunner(None, chunks=["b"]),
        )

        orchestrator = AdkOrchestrator(
            agents=[agent_a, agent_b],
        )

        context = orchestrator.context(
            "INC-1",
            "WF-1",
            {"title": "outage"},
        )

        results = await orchestrator.run(context)

        assert len(results) == 2

        assert [r.agent for r in results] == [
            "first",
            "second",
        ]

        assert all(
            r.status == AgentStatus.SUCCESS
            for r in results
        )

    @pytest.mark.asyncio
    async def test_stop_on_failure(
        self,
    ):

        class FailingRunner(FakeRunner):

            async def run_async(self, **kwargs):
                async for event in super().run_async(**kwargs):
                    yield event
                    raise RuntimeError("boom")

        agent_a = AdkAgent(
            name="first",
            runner_factory=lambda _: FailingRunner(None),
        )

        agent_b = AdkAgent(
            name="second",
            runner_factory=lambda _: FakeRunner(None, chunks=["b"]),
        )

        orchestrator = AdkOrchestrator(
            agents=[agent_a, agent_b],
            stop_on_failure=True,
        )

        context = orchestrator.context(
            "INC-2",
            "WF-2",
        )

        results = await orchestrator.run(context)

        assert len(results) == 1

        assert results[0].status == AgentStatus.FAILURE

        assert results[0].error == "ADK execution failed: boom"

    def test_list_and_count(
        self,
    ):

        agent = AdkAgent(
            name="solo",
            runner_factory=lambda _: FakeRunner(None),
        )

        orchestrator = AdkOrchestrator(agents=[agent])

        assert orchestrator.list_agents() == ["solo"]

        assert orchestrator.agent_count() == 1
