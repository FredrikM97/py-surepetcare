class AuthenticationError(Exception):
    """Raised for authentication failures."""

    pass


class ApiError(Exception):
    """Base exception for all API HTTP errors."""

    def __init__(self, method: str, endpoint: str, status: int, reason: str | None, payload=None):
        self.method = method.upper()
        self.endpoint = endpoint
        self.status = status
        self.reason = reason
        self.payload = payload
        message = (
            f"API error: {self.method} {self.endpoint} " f"returned {self.status} {self.reason or ''}".strip()
        )
        super().__init__(message)
