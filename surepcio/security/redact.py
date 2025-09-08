def redact_sensitive(data, keys_to_redact=None, mask="***REDACTED***"):
    """
    Recursively redact sensitive fields in a nested dict or list.
    By default, redacts common sensitive keys including 'name'.
    """
    if keys_to_redact is None:
        keys_to_redact = {"email_address", "share_code", "code", "name"}
    if isinstance(data, dict):
        return {
            k: (mask if k in keys_to_redact else redact_sensitive(v, keys_to_redact, mask))
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [redact_sensitive(item, keys_to_redact, mask) for item in data]
    else:
        return data