from threading import Lock

from app.infrastructure.ai.registry.provider_metadata import (
    ProviderCapability,
    ProviderMetadata,
)


class ProviderMetadataRegistry:
    """
    Stores and manages metadata for all registered AI providers.

    Metadata is registered by provider name and consumed by
    the routing engine for cost-aware and capability-aware
    provider selection.

    Thread-safe.
    """

    def __init__(self) -> None:
        self._metadata: dict[str, ProviderMetadata] = {}

        self._lock = Lock()

    def register(
        self,
        metadata: ProviderMetadata,
    ) -> None:
        """
        Register metadata for an AI provider.
        """

        with self._lock:
            self._metadata[metadata.name.lower()] = metadata

    def get(
        self,
        name: str,
    ) -> ProviderMetadata:
        """
        Retrieve metadata for a provider by name.
        """

        with self._lock:
            metadata = self._metadata.get(name.lower())

        if metadata is None:
            raise ValueError(
                f"Metadata for AI provider '{name}' is not registered."
            )

        return metadata

    def exists(
        self,
        name: str,
    ) -> bool:
        with self._lock:
            return name.lower() in self._metadata

    def list(self) -> list[str]:
        with self._lock:
            return sorted(self._metadata.keys())

    def all(self) -> list[ProviderMetadata]:
        """
        Returns metadata for all registered providers.
        """

        with self._lock:
            return [
                self._metadata[name]
                for name in sorted(self._metadata.keys())
            ]

    def with_capability(
        self,
        capability: ProviderCapability,
    ) -> list[ProviderMetadata]:
        """
        Returns metadata for all enabled providers that
        support the given capability.
        """

        with self._lock:
            return [
                metadata
                for name, metadata in sorted(self._metadata.items())
                if metadata.enabled and metadata.supports(capability)
            ]
