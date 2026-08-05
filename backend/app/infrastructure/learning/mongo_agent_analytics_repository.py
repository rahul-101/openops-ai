from app.core.config import settings
from app.infrastructure.learning.agent_analytics import AgentStats
from app.infrastructure.persistence.mongodb import get_database


class MongoAgentAnalyticsRepository:
    """
    MongoDB persistence for agent analytics.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.AGENT_ANALYTICS_COLLECTION
        ]

    def _to_document(self, stats: AgentStats) -> dict:
        return {
            "agent": stats.agent,
            "total_runs": stats.total_runs,
            "successful_runs": stats.successful_runs,
            "failed_runs": stats.failed_runs,
            "total_latency_ms": stats.total_latency_ms,
        }

    def _from_document(self, document: dict) -> AgentStats:
        document.pop("_id", None)
        return AgentStats(**document)

    def save(self, stats: AgentStats) -> None:
        self.collection.replace_one(
            {"agent": stats.agent},
            self._to_document(stats),
            upsert=True,
        )

    def get(self, agent: str) -> AgentStats | None:
        document = self.collection.find_one({"agent": agent})
        if document is None:
            return None
        return self._from_document(document)

    def get_all(self) -> list[AgentStats]:
        cursor = self.collection.find({})
        return [self._from_document(doc) for doc in cursor]

    def clear(self) -> None:
        self.collection.delete_many({})