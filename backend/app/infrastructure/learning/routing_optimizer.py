from dataclasses import dataclass
from threading import Lock


@dataclass
class ProviderPerformance:
    """
    Learned performance for a single provider.
    """

    provider: str

    total_calls: int = 0

    successful_calls: int = 0

    failed_calls: int = 0

    total_latency_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        """
        Returns success percentage.
        """

        if self.total_calls == 0:
            return 100.0

        return (
            self.successful_calls
            / self.total_calls
        ) * 100

    @property
    def average_latency_ms(self) -> float:

        if self.total_calls == 0:
            return 0.0

        return (
            self.total_latency_ms
            / self.total_calls
        )


class RoutingOptimizer:
    """
    Learns provider performance from live feedback and
    improves provider selection over time.
    """

    def __init__(self) -> None:

        self._providers: dict[str, ProviderPerformance] = {}

        self._lock = Lock()

    def register_provider(
        self,
        provider: str,
    ) -> None:

        with self._lock:

            self._providers.setdefault(
                provider,
                ProviderPerformance(provider=provider),
            )

    def record_outcome(
        self,
        *,
        provider: str,
        success: bool,
        latency_ms: float = 0.0,
    ) -> None:
        """
        Records the outcome of a routing attempt.
        """

        with self._lock:

            performance = self._providers.setdefault(
                provider,
                ProviderPerformance(provider=provider),
            )

            performance.total_calls += 1

            performance.total_latency_ms += latency_ms

            if success:
                performance.successful_calls += 1
            else:
                performance.failed_calls += 1

    def get_performance(
        self,
        provider: str,
    ) -> ProviderPerformance:

        with self._lock:

            return self._providers.get(
                provider,
                ProviderPerformance(provider=provider),
            )

    def get_all_performance(self) -> list[ProviderPerformance]:

        with self._lock:

            return list(
                self._providers.values()
            )

    def rank_providers(self) -> list[str]:
        """
        Returns providers ranked best-first using a learned
        score. Lower learned score is better.

        The score blends failure rate (heavily weighted) with
        average latency.
        """

        with self._lock:

            providers = list(
                self._providers.values()
            )

        def learned_score(
            performance: ProviderPerformance,
        ) -> float:
            """
            Learned score.

            Failure rate is weighted most heavily, followed
            by average latency.
            """

            failure_rate = 100.0 - performance.success_rate

            return (
                (failure_rate / 100)
                * self.FAILURE_WEIGHT
                +
                (performance.average_latency_ms / 1000)
                * self.LATENCY_WEIGHT
            )

        providers.sort(key=learned_score)

        return [
            p.provider for p in providers
        ]

    FAILURE_WEIGHT = 0.7

    LATENCY_WEIGHT = 0.3

    def clear(self) -> None:

        with self._lock:
            self._providers.clear()
