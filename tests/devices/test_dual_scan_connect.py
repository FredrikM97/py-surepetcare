# Integration tests for DualScanConnect device (add real integration if/when mock data is available)
from surepetcare.devices.dual_scan_connect import DualScanConnect
from surepetcare.enums import ProductId


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


def test_dual_scan_connect_properties():
    device = DualScanConnect(make_data())
    assert device.product == ProductId.DUAL_SCAN_CONNECT


def test_dual_scan_connect_refresh_with_response():
    device = DualScanConnect(make_data())
    command = device.refresh()
    # Simulate API response
    response = {
        "data": {
            "id": 123,
            "household_id": 456,
            "name": "Updated Device",
            "status": {"online": False, "battery": 5.2},
        }
    }
    result = command.callback(response)
    assert result is device
    assert device._data["name"] == "Updated Device"
    assert device._data["status"]["online"] is False
    assert device._data["status"]["battery"] == 5.2


def test_dual_scan_connect_refresh_no_response():
    device = DualScanConnect(make_data())
    command = device.refresh()
    result = command.callback(None)
    assert result is device
    # Data should not change
    assert device._data["name"] == "Test Device"


def test_dual_scan_connect_properties_full():
    data = make_data()
    data["parent_device_id"] = 789
    device = DualScanConnect(data)
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.parent_device_id == 789
    assert device.product_id == 6
    assert device.product_name == "DUAL_SCAN_CONNECT"
    assert device._available is True
    # Battery level calculation
    assert isinstance(device.battery_level, int)


def test_dual_scan_connect_properties_missing_fields():
    data = {"id": 1, "household_id": 2, "name": "NoStatusDevice"}
    device = DualScanConnect(data)
    assert device._available is None
    assert device.parent_device_id is None
    # Battery level should be None if no status
    assert device.battery_level is None


def test_dual_scan_connect_battery_level_edge_cases():
    # Non-numeric battery value
    data = make_data()
    data["status"]["battery"] = "not_a_number"
    device = DualScanConnect(data)
    assert device.battery_level is None
    # Missing battery key
    data = make_data()
    del data["status"]["battery"]
    device = DualScanConnect(data)
    assert device.battery_level is None
    # Missing status key
    data = make_data()
    del data["status"]
    device = DualScanConnect(data)
    assert device.battery_level is None
