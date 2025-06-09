import pytest

# Integration tests for NoIdDogBowlConnect device (add real integration if/when mock data is available)
from surepetcare.devices.no_id_dog_bowl_connect import NoIdDogBowlConnect
from surepetcare.enums import ProductId


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 0},  # 0 is 0%
    }


def test_no_id_dog_bowl_connect_properties():
    """Test NoIdDogBowlConnect properties."""
    device = NoIdDogBowlConnect(make_data())
    assert device.product == ProductId.NO_ID_DOG_BOWL_CONNECT
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.available is True
    assert device.battery_level == 0


@pytest.mark.skip(reason="refresh not implemented for NoIdDogBowlConnect")
def test_no_id_dog_bowl_connect_refresh():
    pass


@pytest.mark.skip(reason="refresh not implemented for NoIdDogBowlConnect")
def test_no_id_dog_bowl_connect_refresh_no_response():
    pass


def test_no_id_dog_bowl_connect_missing_fields():
    """Test NoIdDogBowlConnect with missing status and battery fields."""
    data = {"id": 1, "household_id": 2, "name": "NoStatusDevice"}
    device = NoIdDogBowlConnect(data)
    assert device.available is None
    assert device.battery_level is None
