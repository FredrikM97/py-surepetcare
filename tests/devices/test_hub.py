import json

import pytest

from surepetcare.devices.hub import Hub
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import patch_client_get
from tests.mock_helpers import recursive_dump


@pytest.fixture
def hub_data():
    data = load_mock_data("tests/fixture/hub.json")
    return data["data"][0]


@pytest.mark.asyncio
async def test_hub(hub_data):
    feeder = Hub({"id": 123, "household_id": 1, "name": "Test Hub"})
    client = patch_client_get(hub_data)
    command = feeder.refresh()
    await client.api(command)
    # Todo add data


@pytest.mark.asyncio
async def test_hub_snapshot(snapshot, hub_data):
    snapshot.snapshot_dir = "tests/snapshots"
    feeder = Hub(hub_data)
    client = patch_client_get(hub_data)
    command = feeder.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(feeder), indent=2), "hub_snapshot.json")
