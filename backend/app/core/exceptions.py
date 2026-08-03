"""
Application exceptions.
"""


class OpenOpsException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundException(OpenOpsException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
        )


class DuplicateResourceException(OpenOpsException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} already exists",
            status_code=409,
        )


class DatabaseException(OpenOpsException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=500,
        )
