# Integration tests for PoseidonConnect device (add real integration if/when mock data is available)
from surepetcare.devices.poseidon_connect import PoseidonConnect
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


def test_poseidon_connect_properties():
    device = PoseidonConnect(DummyClient(), make_data())
    assert device.product == ProductId.POSEIDON_CONNECT
