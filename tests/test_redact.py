import ast
import json
import logging

import pytest

from surepcio.const import DEFAULT_SENSITIVE_FIELDS
from surepcio.security.redact import redact_sensitive


@pytest.fixture
def household_file():
    return "tests/fixture/household.json"


def test_redact_sensitive_fields_in_household(household_file):
    """Test that sensitive fields in household.json are redacted."""

    with open(household_file) as f:
        data = json.load(f)
    redacted = redact_sensitive(data)
    # Recursively check that sensitive fields are redacted
    sensitive_keys = {"email_address", "share_code", "code", "name", "users"}

    def check_redacted(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in sensitive_keys:
                    # Should be redacted (e.g., replaced with '***' or similar)
                    assert (
                        v is None
                        or v == "***REDACTED***"
                        or (isinstance(v, list) and not v)
                        or (isinstance(v, dict) and not v)
                    ), f"Field {k} not redacted: {v}"
                else:
                    check_redacted(v)
        elif isinstance(obj, list):
            for item in obj:
                check_redacted(item)

    check_redacted(redacted)


def test_logging_redacts_sensitive_data(caplog):
    """Test that logging with sensitive data redacts those fields."""

    data = {
        "email_address": "userEmail@derp.se",
        "share_code": "supersecrettoken",
        "code": "somecodexr",
        "feedback": "ok data",
    }
    logger = logging.getLogger("surepcio.security.auth")
    logger.info("Sensitive: %s", data)

    # Check that sensitive fields are redacted in the log output
    for record in caplog.records:
        msg = record.getMessage()
        if msg.startswith("Sensitive: "):
            logged_dict = ast.literal_eval(msg[len("Sensitive: ")])
            for key in DEFAULT_SENSITIVE_FIELDS:
                if key in logged_dict:
                    assert (
                        logged_dict[key] == "***REDACTED***"
                    ), f"Field {key} not redacted: {logged_dict[key]}"
