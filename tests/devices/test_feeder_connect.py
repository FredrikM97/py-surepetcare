import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio.household import Household
from tests.mock_helpers import MockClient
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_file():
    return "tests/fixture/feeder_connect.json"


@pytest.fixture
def household_file():
    return "tests/fixture/household.json"


@pytest.mark.asyncio
async def test_snapshot(snapshot: SnapshotAssertion, household_file, device_file):
    snapshot.snapshot_dir = "tests/snapshots"
    client = MockClient(fixture_file=device_file)
    client.set_mock_response(household_file)
    household = await client.api(Household.get_household(7777))
    client.reset()
    device = (await client.api(household.get_devices()))[0]
    await client.api(device.refresh())
    assert recursive_dump(device) == snapshot
