import json

import pytest

from surepetcare.devices.pet import Pet
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import patch_client_get
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_data():
    data = load_mock_data("tests/fixture/pet.json")
    return data["data"][0]


@pytest.fixture
def device_report_data():
    data = load_mock_data("tests/fixture/pet_report.json")
    return data


@pytest.mark.asyncio
async def test_pet(device_data, device_report_data):
    feeder = Pet(device_data)
    client = patch_client_get(device_report_data)
    command = feeder.refresh()
    await client.api(command)

    # Todo add data checks


@pytest.mark.asyncio
async def test_snapshot(snapshot, device_data, device_report_data):
    snapshot.snapshot_dir = "tests/snapshots"
    device = Pet(device_data)
    client = patch_client_get(device_report_data)
    command = device.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(device), indent=2), "pet_snapshot.json")


@pytest.mark.asyncio
async def test_refresh_updates_status_and_control(device_data, device_report_data):
    device = Pet(device_data)
    client = patch_client_get(device_report_data)
    command = device.refresh()
    await client.api(command)
    device_report_data["feeding"]["datapoints"][0]["device_id"] = 1337
    client = patch_client_get(device_report_data)
    command = device.refresh()
    await client.api(command)
    assert device.status.report.feeding[0].device_id == 1337
