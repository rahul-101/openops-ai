class ToolError(Exception):
    """Base exception for the tool framework."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class ToolExecutionError(ToolError):
    """Raised when a tool action fails."""


class ToolApprovalRequiredError(ToolError):
    """Raised when a risky action requires approval."""


class ToolApprovalDeniedError(ToolError):
    """Raised when executing an approval that is not approved."""
