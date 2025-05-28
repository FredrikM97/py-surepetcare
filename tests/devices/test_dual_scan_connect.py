# Integration tests for DualScanConnect device (add real integration if/when mock data is available)
from surepetcare.devices.dual_scan_connect import DualScanConnect
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

def test_dual_scan_connect_properties():
    device = DualScanConnect(DummyClient(), make_data())
    assert device.product == ProductId.DUAL_SCAN_CONNECT