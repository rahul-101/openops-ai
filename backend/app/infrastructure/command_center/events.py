import asyncio
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Optional
from uuid import uuid4

from app.core.config import settings
from app.infrastructure.persistence.mongodb import get_database


class EventType(str, Enum):
    """
    Kinds of events emitted by the operations command center.
    """

    INCIDENT_CREATED = "incident_created"

    ANALYSIS_STARTED = "analysis_started"

    RCA_COMPLETED = "rca_completed"

    DECISION_CREATED = "decision_created"

    TOOL_EXECUTION_STARTED = "tool_execution_started"

    TOOL_EXECUTION_COMPLETED = "tool_execution_completed"

    INCIDENT_RESOLVED = "incident_resolved"


class EventCategory(str, Enum):
    """
    High level grouping of an event.
    """

    INCIDENT = "incident"

    AGENT = "agent"

    EXECUTION = "execution"


@dataclass
class CommandCenterEvent:
    """
    A single event emitted into the command center.
    """

    type: EventType

    incident_id: str = ""

    agent: str = ""

    action: str = ""

    status: str = ""

    duration_ms: float = 0.0

    metadata: dict = field(default_factory=dict)

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    @property
    def category(self) -> EventCategory:

        if self.type in (
            EventType.INCIDENT_CREATED,
            EventType.INCIDENT_RESOLVED,
        ):
            return EventCategory.INCIDENT

        if self.type in (
            EventType.TOOL_EXECUTION_STARTED,
            EventType.TOOL_EXECUTION_COMPLETED,
        ):
            return EventCategory.EXECUTION

        return EventCategory.AGENT

    def to_dict(self) -> dict:

        return {
            "event_id": self.event_id,
            "type": self.type.value,
            "category": self.category.value,
            "incident_id": self.incident_id,
            "agent": self.agent,
            "action": self.action,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "metadata": dict(self.metadata),
            "timestamp": self.timestamp.isoformat(),
        }


class EventPublisher:
    """
    Reusable real-time event publisher.

    Broadcasts workflow, tool, and AI reasoning events to
    subscribed consumers. Supports both synchronous listeners
    and async streaming (Server-Sent Events).
    """

    def __init__(
        self,
        max_history: int = 1000,
    ) -> None:

        self._listeners: list[Callable] = []

        self._streams: set[asyncio.Queue] = set()

        self._history: deque = deque(maxlen=max_history)

        self._lock = Lock()

        self._mongo_repo = None
        if settings.REPOSITORY_TYPE.lower() == "mongo":
            from app.infrastructure.command_center.mongo_event_repository import (
                MongoEventRepository,
            )
            self._mongo_repo = MongoEventRepository()

    # ==========================================================
    # Publishing
    # ==========================================================

    def publish(
        self,
        event: CommandCenterEvent,
    ) -> CommandCenterEvent:
        """
        Emits an event to all listeners and open streams.
        """

        with self._lock:

            self._history.append(event)

            listeners = list(self._listeners)

            streams = set(self._streams)

        if self._mongo_repo is not None:
            self._mongo_repo.insert(event)

        for listener in listeners:

            try:
                listener(event)
            except Exception:
                pass

        for stream in streams:

            self._put_stream(stream, event.to_dict())

        return event

    @staticmethod
    def _put_stream(
        stream: asyncio.Queue,
        payload: dict,
    ) -> None:
        """
        Delivers a payload to an async stream in a thread safe
        way. Uses the queue's bound loop when available so a
        coroutine awaiting stream.get() wakes up even when the
        event was emitted from another thread.
        """

        loop = getattr(stream, "_loop", None)

        if loop is not None:

            loop.call_soon_threadsafe(
                stream.put_nowait,
                payload,
            )

            return

        stream.put_nowait(payload)

    # ==========================================================
    # Sync Listeners
    # ==========================================================

    def subscribe(
        self,
        listener: Callable,
    ) -> None:
        """
        Registers a synchronous listener that receives every
        published event.
        """

        with self._lock:
            self._listeners.append(listener)

    def unsubscribe(
        self,
        listener: Callable,
    ) -> None:

        with self._lock:

            if listener in self._listeners:
                self._listeners.remove(listener)

    # ==========================================================
    # Async Streaming
    # ==========================================================

    def open_stream(self) -> asyncio.Queue:
        """
        Opens a new async stream (asyncio.Queue) that receives
        published events as dicts.
        """

        stream: asyncio.Queue = asyncio.Queue()

        with self._lock:
            self._streams.add(stream)

        return stream

    def close_stream(
        self,
        stream: asyncio.Queue,
    ) -> None:

        with self._lock:
            self._streams.discard(stream)

    # ==========================================================
    # History
    # ==========================================================

    def history(
        self,
        limit: int | None = None,
        *,
        event_type: EventType | None = None,
        incident_id: str | None = None,
    ) -> list[CommandCenterEvent]:

        if self._mongo_repo is not None:
            return self._mongo_repo.history(
                limit=limit,
                event_type=event_type,
                incident_id=incident_id,
            )

        with self._lock:

            events = [
                event
                for event in self._history
                if (
                    event_type is None
                    or event.type == event_type
                )
                and (
                    incident_id is None
                    or event.incident_id == incident_id
                )
            ]

        if limit is not None:
            events = events[-limit:]

        return list(events)

    def history(
        self,
        limit: int | None = None,
        *,
        event_type: EventType | None = None,
        incident_id: str | None = None,
    ) -> list[CommandCenterEvent]:

        if self._mongo_repo is not None:
            return self._mongo_repo.history(
                limit=limit,
                event_type=event_type,
                incident_id=incident_id,
            )

        with self._lock:

            events = [
                event
                for event in self._history
                if (
                    event_type is None
                    or event.type == event_type
                )
                and (
                    incident_id is None
                    or event.incident_id == incident_id
                )
            ]

        if limit is not None:
            events = events[-limit:]

        return list(events)

    def clear(self) -> None:

        with self._lock:
            self._history.clear()

        if self._mongo_repo is not None:
            self._mongo_repo.clear()
