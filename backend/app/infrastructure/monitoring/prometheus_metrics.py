from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class PrometheusMetrics:
    """
    Prometheus metric definitions for AI provider monitoring.

    Metrics are exposed via the /metrics endpoint in the
    Prometheus text exposition format.
    """

    LATENCY_BUCKETS = (
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        30.0,
        60.0,
    )

    def __init__(
        self,
        registry: CollectorRegistry,
    ) -> None:

        self.ai_requests_total = Counter(
            "ai_requests_total",
            "Total AI requests processed.",
            ["provider"],
            registry=registry,
        )

        self.ai_provider_successes_total = Counter(
            "ai_provider_successes_total",
            "Successful AI provider calls.",
            ["provider"],
            registry=registry,
        )

        self.ai_provider_failures_total = Counter(
            "ai_provider_failures_total",
            "Failed AI provider calls.",
            ["provider"],
            registry=registry,
        )

        self.ai_provider_latency_seconds = Histogram(
            "ai_provider_latency_seconds",
            "AI provider latency in seconds.",
            ["provider"],
            buckets=self.LATENCY_BUCKETS,
            registry=registry,
        )

        self.ai_provider_input_tokens_total = Counter(
            "ai_provider_input_tokens_total",
            "Total input tokens consumed.",
            ["provider"],
            registry=registry,
        )

        self.ai_provider_output_tokens_total = Counter(
            "ai_provider_output_tokens_total",
            "Total output tokens generated.",
            ["provider"],
            registry=registry,
        )

        self.ai_provider_cost_usd_total = Counter(
            "ai_provider_cost_usd_total",
            "Total estimated cost in USD.",
            ["provider"],
            registry=registry,
        )

        self.ai_provider_circuit_state = Gauge(
            "ai_provider_circuit_state",
            "Circuit breaker state. 0=closed, 1=half_open, 2=open.",
            ["provider"],
            registry=registry,
        )
