from dataclasses import dataclass, field


@dataclass
class AgentContext:
    """
    Shared execution context passed between agents.

    Agents read from `input`, write shared results into
    `state`, and append to `history` and `recommendations`
    so later agents (and the workflow) can consume them.
    """

    incident_id: str

    workflow_id: str

    input: dict = field(default_factory=dict)

    state: dict = field(default_factory=dict)

    history: list = field(default_factory=list)

    recommendations: list = field(default_factory=list)

    def get(
        self,
        key: str,
        default=None,
    ):
        return self.state.get(key, default)

    def set(
        self,
        key: str,
        value,
    ) -> None:
        self.state[key] = value

    def add_recommendation(
        self,
        text: str,
    ) -> None:
        self.recommendations.append(text)
