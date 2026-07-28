class OpenOpsException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundException(OpenOpsException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
        )