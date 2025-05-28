# Integration tests for PetDoor device (add real integration if/when mock data is available)
from surepetcare.devices.pet_door import PetDoor
from surepetcare.enums import ProductId


class DummyClient:
    pass


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


def test_pet_door_properties():
    device = PetDoor(DummyClient(), make_data())
    assert device.product == ProductId.PET_DOOR
