import json

import pytest

from surepetcare.devices.feeder_connect import FeederConnect
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import patch_client_get
from tests.mock_helpers import recursive_dump


@pytest.fixture
def feeder_data():
    data = load_mock_data("tests/fixture/feeder_connect.json")
    return data["data"][0]


@pytest.mark.asyncio
async def test_feeder_connect(feeder_data):
    feeder = FeederConnect({"id": 123, "household_id": 1, "name": "Test Feeder"})
    client = patch_client_get(feeder_data.copy())
    command = feeder.refresh()
    await client.api(command)
    assert feeder.status.battery == feeder_data["status"]["battery"]
    assert feeder.control.lid == feeder_data["control"]["lid"]


@pytest.mark.asyncio
async def test_feeder_connect_snapshot(snapshot, feeder_data):
    snapshot.snapshot_dir = "tests/snapshots"
    feeder = FeederConnect(feeder_data)
    client = patch_client_get(feeder_data.copy())
    command = feeder.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(feeder), indent=2), "feeder_connect_snapshot.json")


@pytest.mark.asyncio
async def test_feeder_connect_refresh_updates_status_and_control(feeder_data):
    feeder = FeederConnect({"id": 123, "household_id": 1, "name": "Test Feeder"})
    client = patch_client_get(feeder_data.copy())
    command = feeder.refresh()
    await client.api(command)

    feeder_data["status"]["battery"] = 3.5
    feeder_data["control"]["lid"]["close_delay"] = 5
    client = patch_client_get(feeder_data.copy())
    command = feeder.refresh()
    feeder = await client.api(command)
    assert feeder.status.battery == 3.5
    assert feeder.battery_level == 0
    assert feeder.control.lid == {"close_delay": 5}


@pytest.mark.asyncio
async def test_feeder_connect_refresh_none_response_keeps_state(feeder_data):
    feeder = FeederConnect(feeder_data)
    old_battery = feeder.status.battery
    old_lid = feeder.control.lid
    client = patch_client_get(None)
    command = feeder.refresh()
    await client.api(command)
    assert feeder.status.battery == old_battery
    assert feeder.control.lid == old_lid
