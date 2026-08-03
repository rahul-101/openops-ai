from app.application.agents.agent import Agent


class AgentRegistry:
    """
    Stores and manages all registered workflow agents.

    Agents are registered by name and returned in
    execution order via `ordered()`.
    """

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(
        self,
        agent: Agent,
    ) -> None:
        self._agents[agent.name.lower()] = agent

    def get(
        self,
        name: str,
    ) -> Agent:
        agent = self._agents.get(name.lower())

        if agent is None:
            raise ValueError(
                f"Agent '{name}' is not registered."
            )

        return agent

    def exists(
        self,
        name: str,
    ) -> bool:
        return name.lower() in self._agents

    def list(self) -> list[str]:
        return sorted(self._agents.keys())

    def ordered(self) -> list[Agent]:
        """
        Returns agents sorted by execution order (lowest first).
        """

        return sorted(
            self._agents.values(),
            key=lambda agent: agent.metadata.order,
        )

    def __len__(self) -> int:
        return len(self._agents)
