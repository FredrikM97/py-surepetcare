import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio.devices.pet import Pet
from surepcio.household import Household
from tests.mock_helpers import MockClient
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_file():
    return "tests/fixture/pet.json"


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
    pets = await client.api(household.get_pets())
    for pet in pets:
        await client.api(pet.refresh())
        data = recursive_dump(pet)
        data["last_fetched_datetime"] = "<ANY>"
        assert data == snapshot


@pytest.mark.asyncio
async def test_fetch_same_from_date_should_make_datapoints_empty(
    snapshot: SnapshotAssertion, household_file, device_file
):
    snapshot.snapshot_dir = "tests/snapshots"
    client = MockClient(fixture_file=device_file)
    client.set_mock_response(household_file)
    household = await client.api(Household.get_household(7777))
    client.reset()
    pets = await client.api(household.get_pets())
    pet: Pet = next(p for p in pets if p.id == 123455)
    assert pet.last_fetched_datetime is not None
    previous_last_fetched_date = pet.last_fetched_datetime

    pet_refresh_1 = pet.refresh()

    pet_from = pet_refresh_1.params["From"]
    assert pet_from == previous_last_fetched_date
    await client.api(pet.refresh())
    pet_refresh_2 = pet.refresh()
    assert pet_refresh_2.params["From"] == pet.last_fetched_datetime
    assert previous_last_fetched_date != pet.last_fetched_datetime

    assert (
        pet.last_fetched_datetime != previous_last_fetched_date
    )  # Exact time is irrelevant only that we get something from API!

    agg_url = f"https://app-api.production.surehub.io/api/report/household/7777/pet/{pet.id}/aggregate"
    if agg_url in client.session._json_data:
        agg = client.session._json_data[agg_url]
        if "data" in agg and "feeding" in agg["data"]:
            agg["data"]["feeding"]["datapoints"] = []
    await client.api(pet.refresh())
    assert pet.status.report.feeding == []
