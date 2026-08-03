from dataclasses import dataclass, field
from enum import Enum
from threading import Lock


class TaskComplexity(str, Enum):
    """
    Complexity tier of a reasoning task.
    """

    SIMPLE = "simple"

    MODERATE = "moderate"

    COMPLEX = "complex"


@dataclass(frozen=True)
class ModelProfile:
    """
    Static metadata for a model tier used by dynamic selection.
    """

    name: str

    model: str

    provider: str

    input_cost_per_1k_tokens: float = 0.0

    output_cost_per_1k_tokens: float = 0.0

    capabilities: frozenset[str] = field(
        default_factory=frozenset
    )


@dataclass
class ModelSelection:
    """
    Result of selecting a model for a task.
    """

    complexity: TaskComplexity

    model: str

    provider: str

    reason: str = ""

    estimated_cost: float = 0.0

    @property
    def model_name(self) -> str:
        return self.model


class DynamicModelSelector:
    """
    Selects a model based on the complexity of the task.

    - Simple tasks route to cheaper / faster models.
    - Complex reasoning routes to stronger models.
    """

    SIMPLE_CAPABILITIES = frozenset(
        {
            "text_generation",
            "streaming",
        }
    )

    COMPLEX_CAPABILITIES = frozenset(
        {
            "text_generation",
            "structured_output",
            "function_calling",
            "long_context",
        }
    )

    def __init__(self) -> None:

        self._simple: list[ModelProfile] = []

        self._complex: list[ModelProfile] = []

        self._lock = Lock()

    def register_simple_model(
        self,
        *,
        name: str,
        model: str,
        provider: str,
        input_cost_per_1k_tokens: float = 0.0,
        output_cost_per_1k_tokens: float = 0.0,
    ) -> None:

        profile = ModelProfile(
            name=name,
            model=model,
            provider=provider,
            input_cost_per_1k_tokens=input_cost_per_1k_tokens,
            output_cost_per_1k_tokens=output_cost_per_1k_tokens,
            capabilities=self.SIMPLE_CAPABILITIES,
        )

        with self._lock:
            self._simple.append(profile)

    def register_complex_model(
        self,
        *,
        name: str,
        model: str,
        provider: str,
        input_cost_per_1k_tokens: float = 0.0,
        output_cost_per_1k_tokens: float = 0.0,
    ) -> None:

        profile = ModelProfile(
            name=name,
            model=model,
            provider=provider,
            input_cost_per_1k_tokens=input_cost_per_1k_tokens,
            output_cost_per_1k_tokens=output_cost_per_1k_tokens,
            capabilities=self.COMPLEX_CAPABILITIES,
        )

        with self._lock:
            self._complex.append(profile)

    def classify(
        self,
        description: str,
        *,
        severity: str = "low",
        tags: list[str] | None = None,
    ) -> TaskComplexity:
        """
        Classifies a task into a complexity tier based on the
        incident description, severity, and tags.
        """

        text = f"{description} {' '.join(tags or [])}"

        complex_hints = (
            "root cause",
            "multi-service",
            "database",
            "network",
            "cross-service",
            "distributed",
            "transaction",
            "correlation",
            "recovery",
            "rollback",
        )

        complex_hits = sum(
            1
            for hint in complex_hints
            if hint in text.lower()
        )

        high_severity = severity.lower() in (
            "high",
            "critical",
            "sev1",
            "p1",
        )

        if complex_hits >= 2 or (
            complex_hits >= 1 and high_severity
        ):
            return TaskComplexity.COMPLEX

        if complex_hits == 1 or high_severity:
            return TaskComplexity.MODERATE

        return TaskComplexity.SIMPLE

    def select(
        self,
        description: str,
        *,
        severity: str = "low",
        tags: list[str] | None = None,
    ) -> ModelSelection | None:
        """
        Selects the cheapest capable model for the task.
        """

        complexity = self.classify(
            description,
            severity=severity,
            tags=tags,
        )

        if complexity == TaskComplexity.COMPLEX:
            return self._select_from(
                self._complex,
                complexity,
                "complex reasoning requires a stronger model",
            )

        if complexity == TaskComplexity.MODERATE:
            return self._select_from(
                self._complex,
                complexity,
                "moderate reasoning benefits from a stronger model",
            )

        return self._select_from(
            self._simple,
            complexity,
            "simple task routed to a cheaper model",
        )

    def select_from_registry(
        self,
        complexity: TaskComplexity,
        registry,
    ) -> ModelSelection | None:
        """
        Selects a model from a metadata registry (using cost
        aware ordering) for the given complexity.
        """

        if complexity == TaskComplexity.SIMPLE:

            profiles = [
                self._to_profile(registry, name)
                for name in registry.list()
            ]

            return self._select_from(
                [p for p in profiles if p is not None],
                complexity,
                "simple task routed to a cheaper model",
            )

        return self._select_from(
            [
                self._to_profile(registry, name)
                for name in registry.list()
                if self._to_profile(registry, name) is not None
            ],
            complexity,
            (
                "complex reasoning routed to a "
                "stronger capable model"
            ),
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _select_from(
        self,
        profiles: list[ModelProfile],
        complexity: TaskComplexity,
        reason: str,
    ) -> ModelSelection | None:

        with self._lock:
            candidates = list(profiles)

        if not candidates:
            return None

        cheapest = min(
            candidates,
            key=lambda profile: profile.output_cost_per_1k_tokens,
        )

        return ModelSelection(
            complexity=complexity,
            model=cheapest.model,
            provider=cheapest.provider,
            reason=reason,
            estimated_cost=(
                cheapest.input_cost_per_1k_tokens
                + cheapest.output_cost_per_1k_tokens
            ) / 2,
        )

    @staticmethod
    def _to_profile(registry, name: str) -> ModelProfile | None:

        if not registry.exists(name):
            return None

        metadata = registry.get(name)

        return ModelProfile(
            name=metadata.name,
            model=metadata.model,
            provider=metadata.name,
            input_cost_per_1k_tokens=(
                metadata.input_cost_per_1k_tokens
            ),
            output_cost_per_1k_tokens=(
                metadata.output_cost_per_1k_tokens
            ),
            capabilities=frozenset(
                capability.value
                for capability in metadata.capabilities
            ),
        )

    def list_models(self) -> dict[str, list[str]]:

        with self._lock:

            return {
                "simple": [
                    profile.model for profile in self._simple
                ],
                "complex": [
                    profile.model for profile in self._complex
                ],
            }
