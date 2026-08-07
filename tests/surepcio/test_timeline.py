import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import SurePetcareResponse
from surepcio.security.exceptions import UnexpectedDataTypeError
from surepcio.timeline import TimelineEvent
from tests.conftest import object_snapshot


def test_get_timeline_command_params() -> None:
    """get_timeline produces correct endpoint and query params."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline(since_id=42, before_id=99, page_size=10)
    assert cmd.method == "GET"
    assert cmd.endpoint == f"{API_ENDPOINT_PRODUCTION}/timeline/household/7777"
    assert cmd.params == {"since_id": 42, "before_id": 99, "page_size": 10}


def test_get_timeline_command_no_params() -> None:
    """get_timeline with no arguments produces empty params."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline()
    assert cmd.params == {}


def test_get_timeline_parse_empty_response() -> None:
    """get_timeline parse returns empty list when response data is None."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline()
    assert cmd.parse is not None
    result: list[TimelineEvent] = cmd.parse(SurePetcareResponse(data=None))
    assert result == []


def test_get_timeline_parse_invalid_type() -> None:
    """get_timeline parse raises UnexpectedDataTypeError when data is not a list."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline()
    assert cmd.parse is not None
    with pytest.raises(UnexpectedDataTypeError):
        cmd.parse(SurePetcareResponse(data={"data": {"not": "a list"}}))


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["timeline", "household"]])
async def test_timeline_snapshot(
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
) -> None:
    """Timeline events are parsed and match the snapshot."""
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        events: list[TimelineEvent] = await client.api(household.get_timeline())

    for event in events:
        object_snapshot(event, snapshot)
