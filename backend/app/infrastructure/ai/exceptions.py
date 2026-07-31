"""
Provider-independent exception hierarchy for the AI Gateway.

Providers translate SDK- or HTTP-specific errors into these exceptions.
The AIRouter only depends on these domain exceptions.
"""


class AIProviderError(Exception):
    """
    Base exception for all provider errors.
    """


class RetryableProviderError(AIProviderError):
    """
    Temporary error.

    The router may safely try the next provider.
    """


class NonRetryableProviderError(AIProviderError):
    """
    Permanent error.

    The router should stop immediately.
    """


# ---------------------------------------------------------------------
# Retryable
# ---------------------------------------------------------------------


class ProviderTimeoutError(RetryableProviderError):
    """Provider request timed out."""


class ProviderRateLimitError(RetryableProviderError):
    """Provider rate limit exceeded."""


class ProviderUnavailableError(RetryableProviderError):
    """Provider temporarily unavailable."""


# ---------------------------------------------------------------------
# Non Retryable
# ---------------------------------------------------------------------


class AuthenticationError(NonRetryableProviderError):
    """Invalid API key or authentication."""


class InvalidRequestError(NonRetryableProviderError):
    """Invalid request or prompt."""