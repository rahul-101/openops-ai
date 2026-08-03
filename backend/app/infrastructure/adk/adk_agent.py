"""
Google ADK agent adapter.

Adapts a `google.adk.agents.Agent` to the OpenOps `Agent`
contract. The adapter is built lazily: the ADK agent is only
constructed when `build()` is called so the bridge stays
importable even when google-adk is not installed.

Running an ADK agent requires a session. The adapter creates
an in-memory session per execution and streams the model
events, joining the final text response into the shared agent
context.
"""

from typing import Any

from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)


class AdkAgent(Agent):
    """
    Wraps a Google ADK agent so it can be executed through the
    shared agent framework.

    The underlying ADK agent is created lazily on first
    execution. ADK-specific configuration (model, instruction,
    tools) is captured at construction time.
    """

    def __init__(
        self,
        name: str,
        instruction: str = "",
        model: str | None = None,
        description: str = "",
        order: int = 100,
        version: str = "1.0.0",
        runner_factory: Any = None,
        tools: list | None = None,
    ) -> None:

        super().__init__(
            AgentMetadata(
                name=name,
                description=description,
                order=order,
                version=version,
            )
        )

        self.instruction = instruction
        self.model = model
        self.tools = tools or []
        self._runner_factory = runner_factory
        self._adk_agent = None
        self._adk_runner = None
        self._adk_error: str | None = None

    # ==========================================================
    # Lazy ADK construction
    # ==========================================================

    def _ensure_adk(self) -> None:
        """
        Imports and builds the underlying google-adk agent and
        runner on first use. Missing dependency surfaces as a
        clear error message instead of an import crash.
        """

        if self._adk_agent is not None:
            return

        try:
            from google.adk.agents import Agent as AdkAgent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
        except ImportError as ex:
            self._adk_error = (
                "google-adk is not installed. "
                "Install it with `pip install google-adk`."
            )
            raise RuntimeError(self._adk_error) from ex

        model = self.model or AdkAgent.DEFAULT_MODEL

        self._adk_agent = AdkAgent(
            name=self.name,
            instruction=self.instruction,
            model=model,
            tools=self.tools,
        )

        if self._runner_factory is not None:
            self._adk_runner = self._runner_factory(
                self._adk_agent
            )
            return

        session_service = InMemorySessionService()
        self._adk_runner = Runner(
            agent=self._adk_agent,
            session_service=session_service,
        )

    @property
    def adk_agent(self):
        self._ensure_adk()
        return self._adk_agent

    @property
    def adk_runner(self):
        self._ensure_adk()
        return self._adk_runner

    # ==========================================================
    # Agent contract
    # ==========================================================

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:

        try:
            self._ensure_adk()
        except RuntimeError as ex:
            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error=str(ex),
            )

        user_input = self._render_user_input(context)

        try:
            text = await self._run_adk(user_input)
        except Exception as ex:
            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error=f"ADK execution failed: {ex}",
            )

        output = {"text": text, "agent": self.name}

        context.set(self.name, output)
        context.add_recommendation(text)

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output=output,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _render_user_input(
        self,
        context: AgentContext,
    ) -> str:
        """
        Serialises the incident context into the user turn text.
        """

        lines = [
            f"Incident: {context.incident_id}",
            f"Workflow: {context.workflow_id}",
        ]

        for key, value in context.input.items():
            lines.append(f"{key}: {value}")

        for key, value in context.state.items():
            if key == self.name:
                continue
            lines.append(f"{key}: {value}")

        return "\n".join(lines)

    async def _run_adk(
        self,
        user_input: str,
    ) -> str:
        """
        Streams events from the ADK runner and joins the model
        text responses into a single string.
        """

        from google.adk.sessions import (
            InMemorySessionService,
        )
        from google.genai import types

        session_service = InMemorySessionService()

        session = session_service.create_session_sync(
            app_name="openops",
            user_id="user",
            state={},
        )

        user_content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)],
        )

        chunks: list[str] = []

        async for event in self._adk_runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=user_content,
        ):

            if event.is_final_response():
                chunks.append(event.content.parts[0].text)

        return "\n".join(chunks)
