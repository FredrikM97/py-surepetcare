from surepetcare.devices.base import SurepyDevice
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


class DummyDevice(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.HUB


def test_surepydevice_properties():
    device = DummyDevice(DummyClient(), make_data())
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.online is True
    assert device.product_id == ProductId.HUB.value
    assert device.product_name == "HUB"
    assert device.raw_data["id"] == 123
    assert str(device).startswith("<DummyDevice id=123>")


def test_battery_level_full():
    device = DummyDevice(DummyClient(), make_data())
    device._data["status"]["battery"] = 6.4
    assert device.battery_level == 100


def test_battery_level_low():
    device = DummyDevice(DummyClient(), make_data())
    device._data["status"]["battery"] = 0.0
    assert device.battery_level == 0


def test_battery_level_invalid():
    device = DummyDevice(DummyClient(), make_data())
    device._data["status"]["battery"] = "not_a_number"
    assert device.battery_level is None


def test_battery_level_missing():
    device = DummyDevice(DummyClient(), make_data())
    device._data["status"].pop("battery")
    assert device.battery_level is None
