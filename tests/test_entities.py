import pytest

from tests.mock_helpers import MockSurePetcareClient


@pytest.mark.asyncio
async def test_pet_entity():
    household_id = 7777
    client = MockSurePetcareClient("tests/mock_data/mock_entity_pet.json")

    pets = await client.get_pets(household_id)
    pet = pets[0]
    assert pet.household_id == household_id
    assert pet.id == 123455
    assert pet.name == "Lilo"
    assert pet.tag == 60972
    feeding = pet.feeding()

    assert feeding.device_id == 271836
    assert feeding.tag == 60972
    assert feeding.change == [-2.24, 0]
    assert feeding.time == "2024-03-13T17:47:17+00:00"
