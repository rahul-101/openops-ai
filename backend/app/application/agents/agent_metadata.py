from dataclasses import dataclass


@dataclass(frozen=True)
class AgentMetadata:
    """
    Static metadata describing an agent.

    `order` controls execution order inside the orchestrator.
    Lower values execute first.
    """

    name: str

    description: str

    order: int = 100

    version: str = "1.0.0"
