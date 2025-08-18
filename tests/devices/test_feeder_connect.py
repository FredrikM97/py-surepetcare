import json

import pytest

from surepetcare.devices.feeder_connect import FeederConnect
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import patch_client_get
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_data():
    data = load_mock_data("tests/fixture/feeder_connect.json")
    return data["data"][0]


@pytest.mark.asyncio
async def test_snapshot(snapshot, device_data):
    snapshot.snapshot_dir = "tests/snapshots"
    feeder = FeederConnect(device_data)
    client = patch_client_get(device_data)
    command = feeder.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(feeder), indent=2), "feeder_connect_snapshot.json")


@pytest.mark.asyncio
async def test_refresh_updates_status_and_control(device_data):
    device = FeederConnect(
        {"id": 123, "household_id": 1, "name": "Test Feeder", "product_id": 1, "parent_device_id": 3}
    )
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)

    device_data["status"]["battery"] = 3.5
    device_data["control"]["lid"]["close_delay"] = 5
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)
    assert device.status.battery == 3.5
    assert device.battery_level == 0
    assert device.control.lid == {"close_delay": 5}


@pytest.mark.asyncio
async def test_refresh_none_response_keeps_state(device_data):
    device = FeederConnect(device_data)
    old_battery = device.status.battery
    old_lid = device.control.lid
    client = patch_client_get(None)
    command = device.refresh()
    await client.api(command)
    assert device.status.battery == old_battery
    assert device.control.lid == old_lid
