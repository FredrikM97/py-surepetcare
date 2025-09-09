import logging

from surepcio.const import DEFAULT_SENSITIVE_FIELDS


def redact_sensitive(data, keys_to_redact=DEFAULT_SENSITIVE_FIELDS, mask="***REDACTED***"):
    """
    Recursively redact sensitive fields in a nested dict or list.
    By default, redacts common sensitive keys including 'name'.
    """
    if isinstance(data, dict):
        return {
            k: (mask if k in keys_to_redact else redact_sensitive(v, keys_to_redact, mask))
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [redact_sensitive(item, keys_to_redact, mask) for item in data]
    else:
        return data


class RedactSensitiveFilter(logging.Filter):
    """A logging filter that redacts sensitive information from log records."""

    def filter(self, record):
        if isinstance(record.args, (dict, list)):
            record.args = (redact_sensitive(record.args),)
        elif isinstance(record.args, tuple):
            record.args = tuple(
                redact_sensitive(arg) if isinstance(arg, (dict, list)) else arg for arg in record.args
            )
        return True
