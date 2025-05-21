import pytest
from surepy.entities.pet import Pet

class DummyClient:
    async def get(self, endpoint, params=None):
        return {"data": {"feeding": [1, 2, 3]}}

@pytest.mark.asyncio
async def test_pet_fetch_and_feeding():
    client = DummyClient()
    pet = Pet(client, "household_id", "pet_id")
    await pet.fetch("2025-01-01", "2025-02-01")
    assert pet.feeding() == [1, 2, 3]

@pytest.mark.asyncio
async def test_pet_feeding_raises_without_fetch():
    client = DummyClient()
    pet = Pet(client, "household_id", "pet_id")
    with pytest.raises(Exception):
        pet.feeding()