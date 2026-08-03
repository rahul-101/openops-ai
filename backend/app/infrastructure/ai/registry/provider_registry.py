from app.application.interfaces.ai_service import AIService


class ProviderRegistry:
    """
    Stores and manages all registered AI providers.

    Providers are registered by name and can be retrieved
    by the AIRouter during request routing.
    """

    def __init__(self) -> None:
        self._providers: dict[str, AIService] = {}

    def register(
        self,
        name: str,
        provider: AIService,
    ) -> None:
        """
        Register an AI provider.
        """

        self._providers[name.lower()] = provider

    def get(
        self,
        name: str,
    ) -> AIService:
        """
        Retrieve a provider by name.
        """

        provider = self._providers.get(name.lower())

        if provider is None:
            raise ValueError(
                f"AI provider '{name}' is not registered."
            )

        return provider

    def exists(
        self,
        name: str,
    ) -> bool:
        return name.lower() in self._providers

    def list(self) -> list[str]:
        return sorted(self._providers.keys())
