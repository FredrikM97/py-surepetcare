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


@pytest.mark.asyncio
async def test_pet(pet_data):
    feeder = Pet({"id": 123, "name": "Test Pet", "household_id": 1})
    client = patch_client_get(pet_data.copy())
    command = feeder.refresh()
    await client.api(command)

    # Todo add data checks


@pytest.mark.asyncio
async def test_snapshot(snapshot, device_data):
    snapshot.snapshot_dir = "tests/snapshots"
    device = Pet(device_data)
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(device), indent=2), "pet_snapshot.json")


@pytest.mark.asyncio
async def test_refresh_updates_status_and_control(device_data):
    device = Pet({"id": 123, "household_id": 1, "name": "Test Feeder"})
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)
    device_data["status"]["report"]["pet_id"] = 5
    client = patch_client_get(device_data)
    command = device.refresh()
    await client.api(command)
    assert device.status.report.pet_id == 5


@pytest.mark.asyncio
async def test_refresh_none_response_keeps_state(device_data):
    device = Pet(device_data)
    old_pet_id = device.status.report.pet_id
    client = patch_client_get(None)
    command = device.refresh()
    await client.api(command)
    assert device.status.report.pet_id == old_pet_id
