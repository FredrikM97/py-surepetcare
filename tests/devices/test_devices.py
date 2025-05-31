import pytest

from surepetcare.devices.device import SurepyDevice
from surepetcare.enums import ProductId


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


class DummyDevice(SurepyDevice):
    def __init__(self, data, product=ProductId.HUB):
        self._product = product
        super().__init__(data)

    @property
    def product(self) -> ProductId:
        return self._product


@pytest.mark.parametrize(
    "product",
    [ProductId.HUB, ProductId.PET_DOOR, ProductId.FEEDER_CONNECT],
)
def test_surepydevice_properties(product):
    data = make_data()
    device = DummyDevice(data, product=product)
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.available is True
    assert device.product_id == product.value
    assert device.product_name == product.name
    assert device.raw_data["id"] == 123
    assert str(device).startswith("<DummyDevice id=123>")


def test_battery_level_full():
    device = DummyDevice(make_data())
    device._data["status"]["battery"] = 6.4
    assert device.battery_level == 100


def test_battery_level_low():
    device = DummyDevice(make_data())
    device._data["status"]["battery"] = 0.0
    assert device.battery_level == 0


def test_battery_level_invalid():
    device = DummyDevice(make_data())
    device._data["status"]["battery"] = "not_a_number"
    assert device.battery_level is None


def test_battery_level_missing():
    device = DummyDevice(make_data())
    device._data["status"].pop("battery")
    assert device.battery_level is None
