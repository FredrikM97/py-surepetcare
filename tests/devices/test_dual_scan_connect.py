import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio.household import Household
from tests.mock_helpers import MockClient
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_file():
    return "tests/fixture/dual_scan_connect.json"


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
    devices = await client.api(household.get_devices())
    for device in devices:
        await client.api(device.refresh())
        data = recursive_dump(device)
        assert data == snapshot
