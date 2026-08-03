from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from app.infrastructure.governance.exceptions import (
    PromptNotFoundError,
    PromptVersionError,
)


@dataclass
class PromptVersion:
    """
    A versioned prompt with metadata.
    """

    name: str

    version: str

    content: str

    metadata: dict = field(default_factory=dict)

    active: bool = False

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class PromptRegistry:
    """
    Versioned store of AI prompt templates.

    Tracks all versions per prompt name and the active
    version used for rendering.
    """

    def __init__(self) -> None:

        self._versions: dict[str, dict[str, PromptVersion]] = {}

        self._active: dict[str, str] = {}

        self._lock = Lock()

    def register(
        self,
        name: str,
        version: str,
        content: str,
        metadata: dict | None = None,
    ) -> PromptVersion:

        with self._lock:

            prompt_versions = self._versions.setdefault(
                name,
                {},
            )

            if version in prompt_versions:
                raise PromptVersionError(
                    f"Version '{version}' already exists for "
                    f"prompt '{name}'."
                )

            is_first = not prompt_versions

            prompt = PromptVersion(
                name=name,
                version=version,
                content=content,
                metadata=metadata or {},
                active=is_first,
            )

            prompt_versions[version] = prompt

            if is_first:
                self._active[name] = version

            return prompt

    def activate(
        self,
        name: str,
        version: str,
    ) -> PromptVersion:

        with self._lock:

            prompt_versions = self._versions.get(name)

            if prompt_versions is None:
                raise PromptNotFoundError(
                    f"Prompt '{name}' not found."
                )

            prompt = prompt_versions.get(version)

            if prompt is None:
                raise PromptNotFoundError(
                    f"Prompt '{name}' version '{version}' not found."
                )

            for existing in prompt_versions.values():
                existing.active = False

            prompt.active = True

            self._active[name] = version

            return prompt

    def get_active(
        self,
        name: str,
    ) -> PromptVersion:

        with self._lock:

            version = self._active.get(name)

            if version is None:
                raise PromptNotFoundError(
                    f"Prompt '{name}' not found."
                )

            return self._versions[name][version]

    def get(
        self,
        name: str,
        version: str,
    ) -> PromptVersion:

        with self._lock:

            prompt_versions = self._versions.get(name)

            if prompt_versions is None:
                raise PromptNotFoundError(
                    f"Prompt '{name}' not found."
                )

            prompt = prompt_versions.get(version)

            if prompt is None:
                raise PromptNotFoundError(
                    f"Prompt '{name}' version '{version}' not found."
                )

            return prompt

    def list_versions(
        self,
        name: str,
    ) -> list[PromptVersion]:

        with self._lock:

            prompt_versions = self._versions.get(name)

            if prompt_versions is None:
                return []

            return sorted(
                prompt_versions.values(),
                key=lambda p: p.version,
            )

    def all(self) -> list[PromptVersion]:

        with self._lock:

            return [
                prompt
                for prompt_versions in self._versions.values()
                for prompt in prompt_versions.values()
            ]
