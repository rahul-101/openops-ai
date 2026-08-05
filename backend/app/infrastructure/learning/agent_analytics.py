from dataclasses import dataclass
from threading import Lock
from typing import Optional

from app.core.config import settings
from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
)


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

        self._store = new_store("agent_analytics")

        self._mongo_repo = None
        if settings.REPOSITORY_TYPE.lower() == "mongo":
            from app.infrastructure.learning.mongo_agent_analytics_repository import (
                MongoAgentAnalyticsRepository,
            )
            self._mongo_repo = MongoAgentAnalyticsRepository()
            # Load from MongoDB
            for stats in self._mongo_repo.get_all():
                self._agents[stats.agent] = stats

        if self._store is not None:

            for record in self._store.all():

                stats = from_jsonable(
                    record,
                    AgentStats,
                )

                if stats is not None:
                    self._agents[stats.agent] = stats

    def _persist(
        self,
        agent: str,
    ) -> None:

        stats = self._agents.get(agent)

        if self._store is not None and stats is not None:
            self._store.save(
                agent,
                to_jsonable(stats),
            )

    def register_agent(
        self,
        agent: str,
    ) -> None:

        with self._lock:

            self._agents.setdefault(
                agent,
                AgentStats(agent=agent),
            )

        self._persist(agent)

        if self._mongo_repo is not None:
            self._mongo_repo.save(self._agents[agent])

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

        self._persist(agent)

        if self._mongo_repo is not None:
            self._mongo_repo.save(stats)

    def get_analytics(
        self,
        agent: str | None = None,
    ) -> list[AgentStats]:

        if self._mongo_repo is not None:
            if agent is not None:
                stats = self._mongo_repo.get(agent)
                if stats is not None:
                    return [stats]
                return [AgentStats(agent=agent)]
            return self._mongo_repo.get_all()

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

        if self._mongo_repo is not None:
            agents = self._mongo_repo.get_all()
        else:
            with self._lock:
                agents = list(self._agents.values())

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

        if self._store is not None:
            self._store.clear()

        if self._mongo_repo is not None:
            self._mongo_repo.clear()
