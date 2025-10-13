import json
import logging

import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio.client import SurePetcareClient
from surepcio.const import DEFAULT_SENSITIVE_FIELDS
from surepcio.const import REDACTED_STRING
from surepcio.household import Household
from surepcio.security.redact import redact_sensitive
from tests.conftest import object_snapshot
from tests.conftest import register_device_api_mocks


@pytest.fixture
def household_file():
    return "tests/fixture/household.json"


def test_redact_sensitive_fields_in_household(household_file):
    """Test that sensitive fields in household.json are redacted."""

    with open(household_file) as f:
        data = json.load(f)
    redacted = redact_sensitive(data)
    # Recursively check that sensitive fields are redacted
    sensitive_keys = DEFAULT_SENSITIVE_FIELDS

    def check_redacted(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in sensitive_keys:
                    assert (
                        v is None
                        or v == REDACTED_STRING
                        or (isinstance(v, list) and not v)
                        or (isinstance(v, dict) and not v)
                    ), f"Field {k} not redacted: {v}"
                else:
                    check_redacted(v)
        elif isinstance(obj, list):
            for item in obj:
                check_redacted(item)

    check_redacted(redacted)


def test_logging_redacts_sensitive_data(caplog, snapshot):
    """Test that logging with sensitive data redacts those fields."""
    data = {
        "email_address": "userEmail@derp.se",
        "share_code": "supersecrettoken",
        "code": "somecodexr",
        "feedback": "ok data",
    }
    logger = logging.getLogger("surepcio.security.auth")
    logger.setLevel(logging.DEBUG)
    logger.info("Sensitive: %s", data)

    # Collect all log messages that start with "Sensitive: "
    messages = [
        record.getMessage() for record in caplog.records if record.getMessage().startswith("Sensitive: ")
    ]
    # Join messages if there are multiple, or just use the first
    object_snapshot(messages, snapshot)


@pytest.mark.asyncio
async def test_snapshot(
    snapshot: SnapshotAssertion, aresponses: aresponses.ResponsesMockServer, mock_all_devices, caplog
):
    logger = logging.getLogger("surepcio")
    logger.setLevel(logging.DEBUG)

    register_device_api_mocks(aresponses, mock_all_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets = await client.api(household.get_pets())
        devices = await client.api(household.get_devices())
        for pet in pets:
            await client.api(pet.refresh())
        for device in devices:
            await client.api(device.refresh())

    # Collect all log messages as a list of strings
    log_messages = [record.getMessage() for record in caplog.records]
    object_snapshot(log_messages, snapshot)
