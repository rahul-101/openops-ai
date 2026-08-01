from __future__ import annotations

from datetime import datetime, timedelta
from threading import Lock

from app.infrastructure.ai.health.circuit_state import (
    CircuitState,
)
from app.infrastructure.ai.health.provider_health import (
    ProviderHealth,
    ProviderStatus,
)


class ProviderHealthService:
    """
    Tracks runtime health of AI providers and implements
    Circuit Breaker behaviour.

    Circuit States

    CLOSED
        Provider receives traffic normally.

    OPEN
        Provider is blocked after repeated failures.

    HALF_OPEN
        Allow a single request to verify recovery.
    """

    FAILURE_THRESHOLD = 3

    SUCCESS_THRESHOLD = 1

    COOLDOWN_PERIOD = timedelta(seconds=60)

    def __init__(self):

        self._providers: dict[str, ProviderHealth] = {}

        self._lock = Lock()

    # ==========================================================
    # Registration
    # ==========================================================

    def register_provider(
        self,
        provider_name: str,
    ) -> None:

        with self._lock:

            if provider_name not in self._providers:

                self._providers[provider_name] = ProviderHealth(
                    provider=provider_name,
                )

    # ==========================================================
    # Success
    # ==========================================================

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

            provider.circuit_state = (
                CircuitState.CLOSED
            )

            provider.opened_at = None

            provider.last_state_change = (
                datetime.utcnow()
            )

            provider.half_open_attempts = 0

    # ==========================================================
    # Failure
    # ==========================================================

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

            #
            # HALF_OPEN failed
            # Immediately reopen the circuit.
            #

            if (
                provider.circuit_state
                == CircuitState.HALF_OPEN
            ):

                self._open_circuit(provider)

                return

            #
            # CLOSED -> OPEN
            #

            if (
                provider.consecutive_failures
                >= self.FAILURE_THRESHOLD
            ):

                provider.status = (
                    ProviderStatus.UNHEALTHY
                )

                self._open_circuit(provider)

    # ==========================================================
    # Routing Decision
    # ==========================================================

    def is_healthy(
        self,
        provider_name: str,
    ) -> bool:

        provider = self._providers[provider_name]

        #
        # Circuit CLOSED
        #

        if (
            provider.circuit_state
            == CircuitState.CLOSED
        ):
            return True

        #
        # Circuit OPEN
        #

        if (
            provider.circuit_state
            == CircuitState.OPEN
        ):

            if (
                provider.retry_after
                and datetime.utcnow()
                >= provider.retry_after
            ):

                provider.circuit_state = (
                    CircuitState.HALF_OPEN
                )

                provider.last_state_change = (
                    datetime.utcnow()
                )

                provider.half_open_attempts = 0

                return True

            return False

        #
        # Circuit HALF_OPEN
        #
        # Allow exactly one request.
        #

        if (
            provider.circuit_state
            == CircuitState.HALF_OPEN
        ):

            if (
                provider.half_open_attempts
                == 0
            ):

                provider.half_open_attempts = 1

                return True

            return False

        return False

    # ==========================================================
    # Helpers
    # ==========================================================

    def _open_circuit(
        self,
        provider: ProviderHealth,
    ) -> None:

        provider.circuit_state = (
            CircuitState.OPEN
        )

        provider.opened_at = datetime.utcnow()

        provider.last_state_change = (
            datetime.utcnow()
        )

        provider.retry_after = (
            datetime.utcnow()
            + self.COOLDOWN_PERIOD
        )

    # ==========================================================
    # Queries
    # ==========================================================

    def get_health(
        self,
        provider_name: str,
    ) -> ProviderHealth:

        return self._providers[provider_name]

    def get_all(
        self,
    ) -> list[ProviderHealth]:

        return list(self._providers.values())