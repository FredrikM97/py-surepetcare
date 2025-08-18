import json

import pytest

from surepetcare.devices.hub import Hub
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import patch_client_get
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_data():
    data = load_mock_data("tests/fixture/hub.json")
    return data["data"][0]


@pytest.mark.asyncio
async def test_snapshot(snapshot, hub_data):
    snapshot.snapshot_dir = "tests/snapshots"
    device = Hub(hub_data)
    client = patch_client_get(hub_data)
    command = device.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(device), indent=2), "hub_snapshot.json")


@pytest.mark.asyncio
async def test_refresh_updates_status_and_control(device_data):
    device = Hub({"id": 123, "household_id": 1, "name": "Test Feeder", "product_id": 1})
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)

    device_data["status"]["battery"] = 3.5
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)
    assert device.status.battery == 3.5
    assert device.battery_level == 0


@pytest.mark.asyncio
async def test_refresh_none_response_keeps_state(device_data):
    device = Hub(device_data)
    old_battery = device.status.battery
    client = patch_client_get(None)
    command = device.refresh()
    await client.api(command)
    assert device.status.battery == old_battery
