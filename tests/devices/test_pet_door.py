# Integration tests for PetDoor device (add real integration if/when mock data is available)
from surepetcare.devices.pet_door import PetDoor
from surepetcare.enums import ProductId


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


def test_pet_door_properties():
    device = PetDoor(make_data())
    assert device.product == ProductId.PET_DOOR


def test_pet_door_refresh_sets_data():
    device = PetDoor(make_data())
    # Simulate a response with 'data' key
    response = {"data": {"foo": "bar"}}
    command = device.refresh()
    # Call the callback directly to simulate API client behavior
    result = command.callback(response)
    assert result is device
    assert device._data == {"foo": "bar"}


def test_pet_door_refresh_none_response():
    device = PetDoor(make_data())
    command = device.refresh()
    # Simulate None response
    result = command.callback(None)
    assert result is device
    # _data should remain unchanged
    assert device._data == make_data()
