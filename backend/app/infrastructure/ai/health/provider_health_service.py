from __future__ import annotations

from datetime import datetime, timedelta
from threading import Lock

from app.infrastructure.ai.health.provider_health import (
    ProviderHealth,
    ProviderStatus,
)


class ProviderHealthService:
    """
    Tracks runtime health of all registered AI providers.

    This service is intentionally stateful and lives in memory.
    """

    FAILURE_THRESHOLD = 3
    SUCCESS_THRESHOLD = 1

    # Cool-down before retrying an unhealthy provider
    COOLDOWN_PERIOD = timedelta(seconds=60)

    def __init__(self):
        self._providers: dict[str, ProviderHealth] = {}
        self._lock = Lock()

    def register_provider(
        self,
        provider_name: str,
    ) -> None:

        with self._lock:

            if provider_name not in self._providers:

                self._providers[provider_name] = ProviderHealth(
                    provider=provider_name
                )

    def mark_success(
        self,
        provider_name: str,
    ) -> None:

        with self._lock:

            provider = self._providers[provider_name]

            provider.consecutive_successes += 1
            provider.consecutive_failures = 0

            provider.last_success = datetime.utcnow()
            provider.updated_at = datetime.utcnow()

            provider.status = ProviderStatus.HEALTHY
            provider.last_error = None
            provider.retry_after = None

    def mark_failure(
        self,
        provider_name: str,
        error: Exception,
    ) -> None:

        with self._lock:

            provider = self._providers[provider_name]

            provider.consecutive_failures += 1
            provider.consecutive_successes = 0

            provider.last_failure = datetime.utcnow()
            provider.updated_at = datetime.utcnow()

            provider.last_error = str(error)

            if (
                provider.consecutive_failures
                >= self.FAILURE_THRESHOLD
            ):

                provider.status = ProviderStatus.UNHEALTHY

                provider.retry_after = (
                    datetime.utcnow()
                    + self.COOLDOWN_PERIOD
                )

    def is_healthy(
        self,
        provider_name: str,
    ) -> bool:

        provider = self._providers[provider_name]

        if provider.status == ProviderStatus.HEALTHY:
            return True

        # Provider is unhealthy but its cooldown has expired.
        # Allow one retry.
        if (
            provider.retry_after is not None
            and datetime.utcnow() >= provider.retry_after
        ):
            return True

        return False

    def get_health(
        self,
        provider_name: str,
    ) -> ProviderHealth:

        return self._providers[provider_name]

    def get_all(
        self,
    ) -> list[ProviderHealth]:

        return list(self._providers.values())