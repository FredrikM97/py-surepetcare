import pytest

from surepetcare.devices.dual_scan_pet_door import DualScanPetDoor
from surepetcare.enums import ProductId

# Integration tests for DualScanPetDoor device (add real integration if/when mock data is available)


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 0},  # 0 is 0%
    }


def test_dual_scan_pet_door_properties():
    """Test DualScanPetDoor properties."""
    device = DualScanPetDoor(make_data())
    assert device.product == ProductId.DUAL_SCAN_PET_DOOR
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.available is True
    assert device.battery_level == 0


@pytest.mark.skip(reason="refresh not implemented for DualScanPetDoor")
def test_dual_scan_pet_door_refresh():
    pass


@pytest.mark.skip(reason="refresh not implemented for DualScanPetDoor")
def test_dual_scan_pet_door_refresh_no_response():
    pass


def test_dual_scan_pet_door_missing_fields():
    """Test DualScanPetDoor with missing status and battery fields."""
    data = {"id": 1, "household_id": 2, "name": "NoStatusDevice"}
    device = DualScanPetDoor(data)
    assert device.available is None
    assert device.battery_level is None
