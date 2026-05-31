class AuthenticationError(Exception):
    """Raised for authentication failures."""

    pass


class InvalidCommandError(ValueError):
    """Raised when a Command is constructed or used incorrectly."""


class InvalidResponseError(ValueError):
    """Raised when an API response has an unexpected or unprocessable format."""


class UnexpectedDataTypeError(InvalidResponseError):
    """Raised when an API response field has an unexpected type.

    Example: expected a dict under 'data' but received a list.
    """

    def __init__(self, field: str, expected: type, got: type) -> None:
        super().__init__(
            f"Expected {expected.__name__} for '{field}' but got {got.__name__}"
        )
        self.field = field
        self.expected = expected
        self.got = got


class NotLoadedError(RuntimeError):
    """Raised when household data (pets, devices) is accessed before it has been fetched."""


class ApiError(Exception):
    """Base exception for all API HTTP errors."""

    def __init__(
        self, method: str, endpoint: str, status: int, reason: str | None, payload=None
    ):
        self.method = method.upper()
        self.endpoint = endpoint
        self.status = status
        self.reason = reason
        self.payload = payload
        message = (
            f"API error: {self.method} {self.endpoint} "
            f"returned {self.status} {self.reason or ''}".strip()
        )
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            "ApiError("
            f"message={str(self)!r}, "
            f"method={self.method!r}, "
            f"endpoint={self.endpoint!r}, "
            f"status={self.status!r}, "
            f"reason={self.reason!r}, "
            f"payload={self.payload!r}"
            ")"
        )
