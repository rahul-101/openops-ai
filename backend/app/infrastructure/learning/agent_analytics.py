from dataclasses import dataclass
from threading import Lock


@dataclass
class AgentStats:
    """
    Analytics for a single agent.
    """

    agent: str

    total_runs: int = 0

    successful_runs: int = 0

    failed_runs: int = 0

    total_latency_ms: float = 0.0

    @property
    def success_rate(self) -> float:

        if self.total_runs == 0:
            return 100.0

        return (
            self.successful_runs
            / self.total_runs
        ) * 100

    @property
    def average_latency_ms(self) -> float:

        if self.total_runs == 0:
            return 0.0

        return (
            self.total_latency_ms
            / self.total_runs
        )


class AgentAnalytics:
    """
    Tracks per agent success, latency and failures.
    """

    def __init__(self) -> None:

        self._agents: dict[str, AgentStats] = {}

        self._lock = Lock()

    def register_agent(
        self,
        agent: str,
    ) -> None:

        with self._lock:

            self._agents.setdefault(
                agent,
                AgentStats(agent=agent),
            )

    def record_run(
        self,
        *,
        agent: str,
        success: bool,
        latency_ms: float = 0.0,
    ) -> None:
        """
        Records a single agent run.
        """

        with self._lock:

            stats = self._agents.setdefault(
                agent,
                AgentStats(agent=agent),
            )

            stats.total_runs += 1

            stats.total_latency_ms += latency_ms

            if success:
                stats.successful_runs += 1
            else:
                stats.failed_runs += 1

    def get_analytics(
        self,
        agent: str | None = None,
    ) -> list[AgentStats]:

        with self._lock:

            if agent is not None:

                return [
                    self._agents.get(
                        agent,
                        AgentStats(agent=agent),
                    )
                ]

            return list(
                self._agents.values()
            )

    def get_agent(
        self,
        agent: str,
    ) -> AgentStats:

        return self.get_analytics(agent=agent)[0]

    def get_summary(self) -> dict:

        with self._lock:

            agents = list(
                self._agents.values()
            )

        if not agents:

            return {
                "total_agents": 0,
                "total_runs": 0,
                "overall_success_rate": 0.0,
            }

        total_runs = sum(
            a.total_runs for a in agents
        )

        total_success = sum(
            a.successful_runs for a in agents
        )

        return {
            "total_agents": len(agents),
            "total_runs": total_runs,
            "overall_success_rate": (
                (total_success / total_runs) * 100
                if total_runs
                else 0.0
            ),
        }

    def clear(self) -> None:

        with self._lock:
            self._agents.clear()
