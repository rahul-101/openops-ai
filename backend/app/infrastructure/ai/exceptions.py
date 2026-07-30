class AIProviderError(Exception):
    """
    Base exception for all AI provider errors.
    """


class RetryableProviderError(AIProviderError):
    """
    A temporary failure.

    The router should try the next provider.
    """


class NonRetryableProviderError(AIProviderError):
    """
    A permanent failure.

    The router should stop immediately.
    """


class ProviderUnavailableError(RetryableProviderError):
    """
    Provider is temporarily unavailable.
    """


class ProviderTimeoutError(RetryableProviderError):
    """
    Provider request timed out.
    """


class ProviderRateLimitError(RetryableProviderError):
    """
    Provider exceeded rate limit.
    """


class AuthenticationError(NonRetryableProviderError):
    """
    Invalid API key or authentication.
    """


class InvalidRequestError(NonRetryableProviderError):
    """
    Invalid prompt or request payload.
    """