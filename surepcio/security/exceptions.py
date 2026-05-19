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
