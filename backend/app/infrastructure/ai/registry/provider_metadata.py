from dataclasses import dataclass, field
from enum import Enum


class ProviderCapability(str, Enum):
    """
    Capabilities that an AI provider can support.

    Used by capability-aware routing to select providers
    that can fulfill the requirements of a request.
    """

    TEXT_GENERATION = "text_generation"

    STRUCTURED_OUTPUT = "structured_output"

    FUNCTION_CALLING = "function_calling"

    STREAMING = "streaming"

    LONG_CONTEXT = "long_context"


@dataclass(frozen=True)
class ProviderMetadata:
    """
    Static metadata describing an AI provider.

    Complements the runtime signals (health, metrics) with
    declarative information such as cost, priority, and
    supported capabilities.

    Consumed by the routing engine for cost-aware and
    capability-aware provider selection.
    """

    name: str

    display_name: str

    model: str

    # ==========================================================
    # Routing Priority
    # ==========================================================

    # Lower values indicate a more preferred provider.
    priority: int = 100

    # ==========================================================
    # Cost (USD per 1K tokens)
    # ==========================================================

    input_cost_per_1k_tokens: float = 0.0

    output_cost_per_1k_tokens: float = 0.0

    # ==========================================================
    # Limits
    # ==========================================================

    max_context_tokens: int = 8192

    # ==========================================================
    # Capabilities
    # ==========================================================

    capabilities: frozenset[ProviderCapability] = field(
        default_factory=frozenset,
    )

    # ==========================================================
    # Availability
    # ==========================================================

    enabled: bool = True

    def supports(
        self,
        capability: ProviderCapability,
    ) -> bool:
        """
        Returns True when the provider supports the capability.
        """

        return capability in self.capabilities

    def blended_cost_per_1k_tokens(self) -> float:
        """
        Returns the average of input and output cost.

        Used by cost-aware routing as a single comparable
        cost signal per provider.
        """

        return (
            self.input_cost_per_1k_tokens
            + self.output_cost_per_1k_tokens
        ) / 2

    def estimated_cost(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimates the cost in USD for the given token counts.
        """

        input_cost = (input_tokens / 1000) * self.input_cost_per_1k_tokens

        output_cost = (output_tokens / 1000) * self.output_cost_per_1k_tokens

        return input_cost + output_cost
