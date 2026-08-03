from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock


@dataclass
class ActivityEntry:
    """
    A single AI activity record.
    """

    agent: str

    task: str

    status: str

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class ActivitySnapshot:
    """
    Current state of the AI activity feed.
    """

    active_agents: list[str] = field(default_factory=list)

    current_tasks: list[str] = field(default_factory=list)

    completed_actions: int = 0

    failures: int = 0


class ActivityFeed:
    """
    Thread safe feed tracking active agents, current tasks,
    completed actions and failures.
    """

    def __init__(self) -> None:

        self._active: dict[str, str] = {}

        self._completed: int = 0

        self._failures: int = 0

        self._history: list[ActivityEntry] = []

        self._lock = Lock()

    def agent_started(
        self,
        agent: str,
        task: str = "",
    ) -> None:

        with self._lock:
            self._active[agent] = task

            self._history.append(
                ActivityEntry(
                    agent=agent,
                    task=task,
                    status="started",
                )
            )

    def agent_completed(
        self,
        agent: str,
        success: bool = True,
    ) -> None:

        with self._lock:

            self._active.pop(agent, None)

            self._history.append(
                ActivityEntry(
                    agent=agent,
                    task="",
                    status=(
                        "completed" if success else "failed"
                    ),
                )
            )

            if success:
                self._completed += 1
            else:
                self._failures += 1

    def record_action(
        self,
        success: bool,
        *,
        agent: str = "",
        task: str = "",
    ) -> None:

        with self._lock:

            self._history.append(
                ActivityEntry(
                    agent=agent,
                    task=task,
                    status=(
                        "completed" if success else "failed"
                    ),
                )
            )

            if success:
                self._completed += 1
            else:
                self._failures += 1

    def snapshot(self) -> ActivitySnapshot:

        with self._lock:

            return ActivitySnapshot(
                active_agents=list(self._active.keys()),
                current_tasks=list(self._active.values()),
                completed_actions=self._completed,
                failures=self._failures,
            )

    def history(
        self,
        limit: int | None = None,
    ) -> list[ActivityEntry]:

        with self._lock:

            entries = list(self._history)

        if limit is not None:
            entries = entries[-limit:]

        return entries

    def clear(self) -> None:

        with self._lock:

            self._active.clear()

            self._completed = 0

            self._failures = 0

            self._history.clear()
