import logging

from surepcio.const import DEFAULT_SENSITIVE_FIELDS


def redact_sensitive(data, keys_to_redact=DEFAULT_SENSITIVE_FIELDS, mask="***REDACTED***"):
    """
    Recursively redact sensitive fields in a nested dict or list.
    By default, redacts common sensitive keys including 'name'.
    Optimized for large logs: set lookups, early returns, and primitive checks.
    """
    if not isinstance(keys_to_redact, set):
        keys_to_redact = set(keys_to_redact)
    if isinstance(data, dict):
        if not data:
            return data
        return {
            k: (mask if k in keys_to_redact else redact_sensitive(v, keys_to_redact, mask))
            for k, v in data.items()
        }
    elif isinstance(data, list):
        if not data:
            return data
        return [redact_sensitive(item, keys_to_redact, mask) for item in data]
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        return str(data)  # fallback for unknown types


class RedactSensitiveFilter(logging.Filter):
    """A logging filter that redacts sensitive information from log records."""

    def filter(self, record):
        if isinstance(record.args, (dict, list)):
            record.args = (redact_sensitive(record.args),)
        elif isinstance(record.args, tuple):
            if not record.args:
                return True
            record.args = tuple(
                redact_sensitive(arg) if isinstance(arg, (dict, list)) else arg for arg in record.args
            )
        return True
