import json

import pytest

from surepetcare.devices.pet import Pet
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import patch_client_get
from tests.mock_helpers import recursive_dump


@pytest.fixture
def pet_data():
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
async def test_pet_snapshot(snapshot, pet_data):
    snapshot.snapshot_dir = "tests/snapshots"
    feeder = Pet(pet_data)
    client = patch_client_get(pet_data)
    command = feeder.refresh()
    await client.api(command)
    snapshot.assert_match(json.dumps(recursive_dump(feeder), indent=2), "pet_snapshot.json")
