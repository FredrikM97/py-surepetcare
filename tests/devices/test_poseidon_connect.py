# Integration tests for PoseidonConnect device (add real integration if/when mock data is available)
from surepetcare.devices.poseidon_connect import PoseidonConnect
from surepetcare.enums import ProductId
import pytest


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 0},  # 0 is 0%
    }


def test_poseidon_connect_properties():
    """Test PoseidonConnect properties."""
    device = PoseidonConnect(make_data())
    assert device.product == ProductId.POSEIDON_CONNECT
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.available is True
    assert device.battery_level == 0


@pytest.mark.skip(reason="refresh not implemented for PoseidonConnect")
def test_poseidon_connect_refresh():
    pass


@pytest.mark.skip(reason="refresh not implemented for PoseidonConnect")
def test_poseidon_connect_refresh_no_response():
    pass


def test_poseidon_connect_missing_fields():
    """Test PoseidonConnect with missing status and battery fields."""
    data = {"id": 1, "household_id": 2, "name": "NoStatusDevice"}
    device = PoseidonConnect(data)
    assert device.available is None
    assert device.battery_level is None
