from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.infrastructure.command_center.incident_timeline import (
    TimelineEntry,
)
from app.infrastructure.command_center.activity_feed import (
    ActivityEntry,
    ActivitySnapshot,
)
from app.infrastructure.command_center.execution_monitor import (
    AgentExecution,
    ExecutionStatus,
)
from app.infrastructure.persistence.mongodb import get_database


class MongoTimelineRepository:
    """
    MongoDB persistence for incident timeline entries.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.TIMELINE_COLLECTION
        ]

    def _to_document(self, incident_id: str, entry: TimelineEntry) -> dict:
        return {
            "incident_id": incident_id,
            "timestamp": entry.timestamp,
            "agent": entry.agent,
            "action": entry.action,
            "status": entry.status,
            "duration_ms": entry.duration_ms,
            "metadata": entry.metadata,
        }

    def _from_document(self, document: dict) -> TimelineEntry:
        document.pop("_id", None)
        return TimelineEntry(
            timestamp=document["timestamp"],
            agent=document["agent"],
            action=document["action"],
            status=document.get("status", ""),
            duration_ms=document.get("duration_ms", 0.0),
            metadata=document.get("metadata", {}),
        )

    def record(self, incident_id: str, entry: TimelineEntry) -> None:
        self.collection.insert_one(self._to_document(incident_id, entry))

    def get(self, incident_id: str) -> list[TimelineEntry]:
        cursor = self.collection.find(
            {"incident_id": incident_id}
        ).sort("timestamp", 1)
        return [self._from_document(doc) for doc in cursor]

    def get_incidents(self) -> list[str]:
        return self.collection.distinct("incident_id")

    def clear(self) -> None:
        self.collection.delete_many({})


class MongoActivityRepository:
    """
    MongoDB persistence for activity feed.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.ACTIVITY_FEED_COLLECTION
        ]

    def _to_document(self, entry: ActivityEntry) -> dict:
        return {
            "agent": entry.agent,
            "task": entry.task,
            "status": entry.status,
            "timestamp": entry.timestamp,
        }

    def _from_document(self, document: dict) -> ActivityEntry:
        document.pop("_id", None)
        return ActivityEntry(
            agent=document["agent"],
            task=document.get("task", ""),
            status=document["status"],
            timestamp=document.get("timestamp"),
        )

    def agent_started(self, agent: str, task: str = "") -> None:
        entry = ActivityEntry(
            agent=agent, task=task, status="started"
        )
        self.collection.insert_one(self._to_document(entry))

    def agent_completed(self, agent: str, success: bool = True) -> None:
        entry = ActivityEntry(
            agent=agent,
            task="",
            status="completed" if success else "failed",
        )
        self.collection.insert_one(self._to_document(entry))

    def record_action(
        self, success: bool, agent: str = "", task: str = ""
    ) -> None:
        entry = ActivityEntry(
            agent=agent,
            task=task,
            status="completed" if success else "failed",
        )
        self.collection.insert_one(self._to_document(entry))

    def snapshot(self) -> ActivitySnapshot:
        # Get active agents (those with "started" but not "completed"/"failed")
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$agent",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$match": {"latest.status": "started"}}
        ]
        active_docs = list(self.collection.aggregate(pipeline))
        active_agents = [doc["latest"]["agent"] for doc in active_docs]
        current_tasks = [
            doc["latest"].get("task", "") for doc in active_docs
        ]

        # Count completed and failed
        completed = self.collection.count_documents(
            {"status": "completed"}
        )
        failures = self.collection.count_documents(
            {"status": "failed"}
        )

        return ActivitySnapshot(
            active_agents=active_agents,
            current_tasks=current_tasks,
            completed_actions=completed,
            failures=failures,
        )

    def history(self, limit: Optional[int] = None) -> list[ActivityEntry]:
        cursor = self.collection.find({}).sort("timestamp", -1)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [self._from_document(doc) for doc in cursor]

    def clear(self) -> None:
        self.collection.delete_many({})


class MongoExecutionMonitorRepository:
    """
    MongoDB persistence for execution monitor.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.EXECUTION_MONITOR_COLLECTION
        ]

    def _to_document(self, execution: AgentExecution) -> dict:
        return {
            "execution_id": execution.execution_id,
            "agent": execution.agent,
            "task": execution.task,
            "incident_id": execution.incident_id,
            "status": execution.status.value,
            "start_time": execution.start_time,
            "completion_time": execution.completion_time,
            "duration_ms": execution.duration_ms,
            "error": execution.error,
        }

    def _from_document(self, document: dict) -> AgentExecution:
        document.pop("_id", None)
        execution = AgentExecution(
            agent=document["agent"],
            execution_id=document["execution_id"],
            task=document.get("task", ""),
            incident_id=document.get("incident_id", ""),
            status=ExecutionStatus(document["status"]),
            start_time=document.get("start_time"),
            completion_time=document.get("completion_time"),
            duration_ms=document.get("duration_ms", 0.0),
            error=document.get("error"),
        )
        return execution

    def save(self, execution: AgentExecution) -> None:
        self.collection.replace_one(
            {"execution_id": execution.execution_id},
            self._to_document(execution),
            upsert=True,
        )

    def get(self, execution_id: str) -> AgentExecution | None:
        document = self.collection.find_one(
            {"execution_id": execution_id}
        )
        if document is None:
            return None
        return self._from_document(document)

    def list(
        self,
        status: Optional[ExecutionStatus] = None,
        incident_id: Optional[str] = None,
    ) -> list[AgentExecution]:
        query = {}
        if status is not None:
            query["status"] = status.value
        if incident_id is not None:
            query["incident_id"] = incident_id

        cursor = self.collection.find(query).sort("start_time", -1)
        return [self._from_document(doc) for doc in cursor]

    def summary(self) -> dict:
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        counts = {doc["_id"]: doc["count"] for doc in self.collection.aggregate(pipeline)}

        running = counts.get("running", 0)
        completed = counts.get("completed", 0)
        failed = counts.get("failed", 0)
        total = running + completed + failed

        return {
            "total": total,
            "running": running,
            "completed": completed,
            "failed": failed,
            "success_rate": (
                (completed / (completed + failed)) * 100
                if (completed + failed)
                else 0.0
            ),
        }

    def clear(self) -> None:
        self.collection.delete_many({})


class MongoDashboardRepository:
    """
    MongoDB persistence for dashboard metrics.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.DASHBOARD_COLLECTION
        ]

    def record_event(self, event_data: dict) -> None:
        self.collection.update_one(
            {"_id": "dashboard"},
            {"$inc": {
                "model_usage." + event_data.get("model", "unknown"): 1,
                "input_tokens": event_data.get("input_tokens", 0),
                "output_tokens": event_data.get("output_tokens", 0),
                "cost_usd": event_data.get("cost_usd", 0.0),
                "successful_actions": 1 if event_data.get("success") else 0,
                "failed_actions": 0 if event_data.get("success") else 1,
            }},
            upsert=True,
        )

    def record_ai_usage(
        self,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        self.collection.update_one(
            {"_id": "dashboard"},
            {"$inc": {
                "model_usage." + model: 1,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
            }},
            upsert=True,
        )

    def get_model_usage(self) -> dict[str, int]:
        doc = self.collection.find_one({"_id": "dashboard"})
        if doc is None:
            return {}
        return doc.get("model_usage", {})

    def get_token_counts(self) -> tuple[int, int]:
        doc = self.collection.find_one({"_id": "dashboard"})
        if doc is None:
            return 0, 0
        return (
            doc.get("input_tokens", 0),
            doc.get("output_tokens", 0),
        )

    def get_cost(self) -> float:
        doc = self.collection.find_one({"_id": "dashboard"})
        if doc is None:
            return 0.0
        return doc.get("cost_usd", 0.0)

    def get_action_counts(self) -> tuple[int, int]:
        doc = self.collection.find_one({"_id": "dashboard"})
        if doc is None:
            return 0, 0
        return (
            doc.get("successful_actions", 0),
            doc.get("failed_actions", 0),
        )

    def clear(self) -> None:
        self.collection.delete_many({})