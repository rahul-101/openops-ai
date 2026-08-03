from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

import yaml

from app.infrastructure.aiops.event_ingestion import (
    NormalizedEvent,
)


@dataclass
class PlaybookStep:
    """
    A single action within a remediation playbook.
    """

    name: str

    tool: str

    action: str

    parameters: dict = field(default_factory=dict)

    risk_level: str = "medium"

    auto_execute: bool = False


@dataclass
class PlaybookMatch:
    """
    Matching criteria used to select a playbook.
    """

    source: str | None = None

    severities: list[str] = field(default_factory=list)

    tags: list[str] = field(default_factory=list)

    def matches(
        self,
        event: NormalizedEvent,
    ) -> bool:

        if (
            self.source
            and event.source.lower() != self.source.lower()
        ):
            return False

        if self.severities:

            expected = {
                s.lower() for s in self.severities
            }

            if event.severity.value not in expected:
                return False

        if self.tags:

            event_tags = {
                t.lower() for t in event.tags
            }

            if not (
                event_tags & {t.lower() for t in self.tags}
            ):
                return False

        return True


@dataclass
class Playbook:
    """
    A reusable remediation workflow.
    """

    name: str

    description: str = ""

    match: PlaybookMatch = field(
        default_factory=PlaybookMatch
    )

    steps: list[PlaybookStep] = field(
        default_factory=list
    )

    version: str = "1.0.0"

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RemediationPlaybookEngine:
    """
    Stores and matches YAML based remediation playbooks.

    Playbooks are reusable workflows executed to remediate
    incidents. Playbook selection is based on matching
    criteria against a normalized event.
    """

    def __init__(self) -> None:

        self._playbooks: dict[str, Playbook] = {}

        self._lock = Lock()

    def load_yaml(
        self,
        content: str,
    ) -> Playbook:
        """
        Parses YAML content into a playbook and registers it.
        """

        data = yaml.safe_load(content)

        return self.register(
            self._parse(data)
        )

    def register(
        self,
        playbook: Playbook,
    ) -> Playbook:

        with self._lock:
            self._playbooks[playbook.name] = playbook

        return playbook

    def get(
        self,
        name: str,
    ) -> Playbook | None:

        with self._lock:
            return self._playbooks.get(name)

    def list(self) -> list[Playbook]:

        with self._lock:
            return list(self._playbooks.values())

    def find(
        self,
        event: NormalizedEvent,
    ) -> Playbook | None:
        """
        Returns the best matching playbook for an event.
        """

        with self._lock:

            for playbook in self._playbooks.values():

                if playbook.match.matches(event):
                    return playbook

            return None

    def clear(self) -> None:

        with self._lock:
            self._playbooks.clear()

    # ==========================================================
    # Parsing
    # ==========================================================

    @staticmethod
    def _parse(
        data: dict,
    ) -> Playbook:

        match_data = data.get("match", {}) or {}

        steps = [
            PlaybookStep(
                name=step.get("name", ""),
                tool=step.get("tool", ""),
                action=step.get("action", ""),
                parameters=step.get("parameters", {}) or {},
                risk_level=step.get(
                    "risk_level",
                    "medium",
                ),
                auto_execute=step.get(
                    "auto_execute",
                    False,
                ),
            )
            for step in data.get("steps", []) or []
        ]

        return Playbook(
            name=data.get("name", ""),
            description=data.get("description", ""),
            match=PlaybookMatch(
                source=match_data.get("source"),
                severities=list(
                    match_data.get("severities", []) or []
                ),
                tags=list(
                    match_data.get("tags", []) or []
                ),
            ),
            steps=steps,
            version=data.get("version", "1.0.0"),
        )
