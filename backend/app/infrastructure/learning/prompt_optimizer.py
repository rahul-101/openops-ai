from dataclasses import dataclass
from threading import Lock


@dataclass
class PromptPerformance:
    """
    Learned performance of a single prompt version.
    """

    prompt_name: str

    version: str

    total_evaluations: int = 0

    successful_evaluations: int = 0

    total_latency_ms: float = 0.0

    total_tokens: int = 0

    @property
    def success_rate(self) -> float:

        if self.total_evaluations == 0:
            return 0.0

        return (
            self.successful_evaluations
            / self.total_evaluations
        ) * 100

    @property
    def average_latency_ms(self) -> float:

        if self.total_evaluations == 0:
            return 0.0

        return (
            self.total_latency_ms
            / self.total_evaluations
        )


class PromptOptimizer:
    """
    Scores prompt versions based on observed performance and
    selects the best prompt for a task.
    """

    SUCCESS_WEIGHT = 0.6

    LATENCY_WEIGHT = 0.25

    TOKEN_WEIGHT = 0.15

    def __init__(self) -> None:

        self._prompts: dict[str, dict[str, PromptPerformance]] = {}

        self._lock = Lock()

    def register_prompt(
        self,
        prompt_name: str,
        version: str,
    ) -> None:

        with self._lock:

            self._prompts.setdefault(
                prompt_name,
                {},
            ).setdefault(
                version,
                PromptPerformance(
                    prompt_name=prompt_name,
                    version=version,
                ),
            )

    def record_evaluation(
        self,
        *,
        prompt_name: str,
        version: str,
        success: bool,
        latency_ms: float = 0.0,
        tokens: int = 0,
    ) -> None:
        """
        Records the outcome of a prompt evaluation.
        """

        with self._lock:

            versions = self._prompts.setdefault(
                prompt_name,
                {},
            )

            performance = versions.setdefault(
                version,
                PromptPerformance(
                    prompt_name=prompt_name,
                    version=version,
                ),
            )

            performance.total_evaluations += 1

            performance.total_latency_ms += latency_ms

            performance.total_tokens += tokens

            if success:
                performance.successful_evaluations += 1

    def get_performance(
        self,
        prompt_name: str,
        version: str,
    ) -> PromptPerformance:

        with self._lock:

            return (
                self._prompts.get(prompt_name, {})
                .get(
                    version,
                    PromptPerformance(
                        prompt_name=prompt_name,
                        version=version,
                    ),
                )
            )

    def _score(
        self,
        performance: PromptPerformance,
    ) -> float:
        """
        Higher score is better.

        Blends success rate, inverse latency and inverse
        token usage.
        """

        success = performance.success_rate / 100

        latency_factor = 1.0 / (
            1.0 + performance.average_latency_ms / 1000
        )

        token_factor = 1.0 / (
            1.0 + performance.total_tokens
        )

        return (
            success * self.SUCCESS_WEIGHT
            + latency_factor * self.LATENCY_WEIGHT
            + token_factor * self.TOKEN_WEIGHT
        )

    def get_best_version(
        self,
        prompt_name: str,
    ) -> str | None:
        """
        Returns the highest scoring version for a prompt.
        """

        with self._lock:

            versions = self._prompts.get(
                prompt_name,
                {},
            )

        if not versions:
            return None

        best = max(
            versions.values(),
            key=self._score,
        )

        return best.version

    def list_versions(
        self,
        prompt_name: str,
    ) -> list[PromptPerformance]:

        with self._lock:

            return list(
                self._prompts.get(prompt_name, {}).values()
            )

    def clear(self) -> None:

        with self._lock:
            self._prompts.clear()
