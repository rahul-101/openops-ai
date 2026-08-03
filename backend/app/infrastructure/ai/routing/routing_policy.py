from abc import ABC, abstractmethod


class RoutingPolicy(ABC):
    """
    Defines how AI providers are selected and prioritized.
    """

    @abstractmethod
    def get_provider_priority(self) -> list[str]:
        """
        Returns the providers in priority order.

        Example:
            ["gemini", "openrouter"]
        """
        raise NotImplementedError

    def select_provider(self) -> str:
        """
        Returns the highest-priority provider.

        This preserves backward compatibility for existing code.
        """
        priority = self.get_provider_priority()

        if not priority:
            raise ValueError("Routing policy returned no providers.")

        return priority[0]
