# Integration tests for NoIdDogBowlConnect device (add real integration if/when mock data is available)
from surepetcare.devices.no_id_dog_bowl_connect import NoIdDogBowlConnect
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


def test_no_id_dog_bowl_connect_properties():
    device = NoIdDogBowlConnect(DummyClient(), make_data())
    assert device.product == ProductId.NO_ID_DOG_BOWL_CONNECT
