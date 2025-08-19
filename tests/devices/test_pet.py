import json

import pytest

from surepetcare.household import Household
from tests.mock_helpers import MockClient
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_file():
    return "tests/fixture/pet.json"


@pytest.fixture
def household_file():
    return "tests/fixture/household.json"


@pytest.mark.asyncio
async def test_snapshot(snapshot, household_file, device_file):
    # snapshot.snapshot_dir = "tests/snapshots"
    client = MockClient(fixture_file=device_file)
    client.set_mock_response(household_file)
    household = await client.api(Household.get_household(7777))
    client.reset()
    pet = (await client.api(household.get_pets()))[0]
    await client.api(pet.refresh())
    result = json.dumps(recursive_dump(pet), indent=2)
    assert result == snapshot
