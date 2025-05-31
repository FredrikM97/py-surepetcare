# Integration tests for DualScanPetDoor device (add real integration if/when mock data is available)
from surepetcare.devices.dual_scan_pet_door import DualScanPetDoor
from surepetcare.enums import ProductId


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


def test_dual_scan_pet_door_properties():
    device = DualScanPetDoor(make_data())
    assert device.product == ProductId.DUAL_SCAN_PET_DOOR
