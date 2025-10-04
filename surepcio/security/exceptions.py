class AuthenticationError(Exception):
    pass


class ValidationMissingFieldsError(Exception):
    """Raised when required fields are missing during model validation."""

    pass
