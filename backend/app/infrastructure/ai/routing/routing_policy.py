from abc import ABC, abstractmethod


class RoutingPolicy(ABC):
    """
    Defines how an AI provider is selected.
    """

    @abstractmethod
    def select_provider(self) -> str:
        """
        Returns the provider name that should handle the request.
        """
        raise NotImplementedError