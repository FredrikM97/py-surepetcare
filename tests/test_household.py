import pytest

from surepetcare.entities.household import HouseholdMixin


class DummyClient(HouseholdMixin):
    def __init__(self, get_result):
        self._get_result = get_result

    async def get(self, endpoint, params=None):
        return self._get_result


@pytest.mark.asyncio
async def test_get_household():
    client = DummyClient({"id": 1, "name": "TestHouse"})
    result = await client.get_household(1)
    assert result["id"] == 1
    assert result["name"] == "TestHouse"


@pytest.mark.asyncio
async def test_get_households():
    client = DummyClient({"data": [{"id": 1}, {"id": 2}]})
    result = await client.get_households()
    assert isinstance(result, list)
    assert result[0]["id"] == 1


@pytest.mark.asyncio
async def test_get_devices():
    # Simulate two devices with valid product_ids
    class DummyEnum:
        name = "dummy"

    class DummyDevice:
        def __init__(self, client, device):
            self.device = device

    def fake_load_device_class(product_id):
        return DummyDevice

    import surepetcare.entities.household as hh

    orig = hh.load_device_class
    hh.load_device_class = fake_load_device_class
    client = DummyClient({"data": [{"product_id": 1}, {"product_id": 3}]})
    result = await client.get_devices([1])
    assert len(result) == 2
    hh.load_device_class = orig


@pytest.mark.asyncio
async def test_get_product():
    client = DummyClient({"foo": "bar"})
    result = await client.get_product(1, 2)
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_get_households_devices():
    # Simulate two households, each with one device
    class DummyDevice:
        def __init__(self, client, device):
            self.device = device

    def fake_load_device_class(product_id):
        return DummyDevice

    import surepetcare.entities.household as hh

    orig = hh.load_device_class
    hh.load_device_class = fake_load_device_class
    client = DummyClient({"data": [{"id": 1}, {"id": 2}]})

    async def async_get_devices(household_ids):
        return [DummyDevice(client, {"id": hid}) for hid in household_ids]

    async def async_get_households():
        return [{"id": 1}, {"id": 2}]

    client.get_devices = async_get_devices
    client.get_households = async_get_households
    result = await client.get_households_devices()
    assert len(result) == 2
    hh.load_device_class = orig


@pytest.mark.asyncio
async def test_get_households_pets():
    class DummyPet:
        def __init__(self, client, pet):
            self.pet = pet

    client = DummyClient({})

    async def async_get_households():
        return [{"id": 1}, {"id": 2}]

    async def async_get_pets(household_id):
        return [DummyPet(client, {"id": household_id * 10})]

    client.get_households = async_get_households
    client.get_pets = async_get_pets
    result = await client.get_households_pets()
    assert len(result) == 2
    assert result[0].pet["id"] == 10
    assert result[1].pet["id"] == 20


@pytest.mark.asyncio
async def test_get_pets():
    class DummyPet:
        def __init__(self, client, pet):
            self.pet = pet
            # Set attributes for all keys in the dict for compatibility
            for k, v in pet.items():
                setattr(self, k, v)

    client = DummyClient({})

    async def async_get(endpoint, params=None):
        # Add 'household_id', 'name', and 'tag' (as dict) to each pet dict to avoid TypeError
        return {
            "data": [
                {"id": 1, "household_id": 1, "name": "Pet1", "tag": {"id": "A1"}},
                {"id": 2, "household_id": 1, "name": "Pet2", "tag": {"id": "B2"}},
            ]
        }

    import surepetcare.entities.pet as pet_mod

    orig = pet_mod.Pet
    pet_mod.Pet = DummyPet
    client.get = async_get
    result = await client.get_pets(1)
    assert len(result) == 2
    assert result[0]._id == 1
    assert result[1]._id == 2
    pet_mod.Pet = orig


@pytest.mark.asyncio
async def test_get_devices_skips_non_matching_product_id():
    # Simulate devices with product_ids, only one matches
    class DummyDevice:
        def __init__(self, client, device):
            self.device = device

    def fake_load_device_class(product_id):
        return DummyDevice

    import surepetcare.entities.household as hh

    orig = hh.load_device_class
    hh.load_device_class = fake_load_device_class
    # Only product_id=1 should match
    client = DummyClient({"data": [{"product_id": 1}, {"product_id": 99}]})
    result = await client.get_devices([1])
    assert len(result) == 1
    assert result[0].device["product_id"] == 1
    hh.load_device_class = orig
