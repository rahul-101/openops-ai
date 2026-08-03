from dataclasses import dataclass, field
from threading import Lock


@dataclass(frozen=True)
class ModelOption:
    """
    A model available for cost optimization.
    """

    provider: str

    model: str

    input_cost_per_1k_tokens: float = 0.0

    output_cost_per_1k_tokens: float = 0.0

    capabilities: frozenset[str] = field(
        default_factory=frozenset
    )

    def estimated_cost(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimates the cost in USD for the given token counts.
        """

        input_cost = (
            (input_tokens / 1000)
            * self.input_cost_per_1k_tokens
        )

        output_cost = (
            (output_tokens / 1000)
            * self.output_cost_per_1k_tokens
        )

        return input_cost + output_cost

    def supports_all(
        self,
        required_capabilities: frozenset[str] | set[str],
    ) -> bool:

        if not required_capabilities:
            return True

        return required_capabilities.issubset(
            self.capabilities
        )


class CostOptimizer:
    """
    Chooses the cheapest capable model for a task.
    """

    def __init__(self) -> None:

        self._models: list[ModelOption] = []

        self._lock = Lock()

    def register_model(
        self,
        *,
        provider: str,
        model: str,
        input_cost_per_1k_tokens: float = 0.0,
        output_cost_per_1k_tokens: float = 0.0,
        capabilities: frozenset[str] | set[str] = frozenset(),
    ) -> ModelOption:

        option = ModelOption(
            provider=provider,
            model=model,
            input_cost_per_1k_tokens=input_cost_per_1k_tokens,
            output_cost_per_1k_tokens=output_cost_per_1k_tokens,
            capabilities=frozenset(capabilities),
        )

        with self._lock:
            self._models.append(option)

        return option

    def list_models(self) -> list[ModelOption]:

        with self._lock:
            return list(self._models)

    def choose(
        self,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        required_capabilities: (
            frozenset[str] | set[str] | None
        ) = None,
        providers: frozenset[str] | set[str] | None = None,
    ) -> ModelOption | None:
        """
        Returns the cheapest model that supports the required
        capabilities. None when no model qualifies.
        """

        required = frozenset(
            required_capabilities or []
        )

        allowed_providers = (
            set(providers) if providers else None
        )

        with self._lock:

            candidates = [
                model
                for model in self._models
                if model.supports_all(required)
                and (
                    allowed_providers is None
                    or model.provider in allowed_providers
                )
            ]

        if not candidates:
            return None

        def total_cost(model: ModelOption) -> float:

            return model.estimated_cost(
                input_tokens,
                output_tokens,
            )

        return min(
            candidates,
            key=total_cost,
        )

    def clear(self) -> None:

        with self._lock:
            self._models.clear()
