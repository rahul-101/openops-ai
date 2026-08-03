class GovernanceError(Exception):
    """Base exception for the governance layer."""


class AuthorizationError(GovernanceError):
    """Raised when a user lacks a required permission."""


class BlockedActionError(GovernanceError):
    """Raised when a high risk action is blocked by policy."""


class PromptNotFoundError(GovernanceError):
    """Raised when a prompt or version is not found."""


class PromptVersionError(GovernanceError):
    """Raised on invalid prompt version operations."""
