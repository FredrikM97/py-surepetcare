import pytest
from surepetcare.devices.device import SurepyDevice
from surepetcare.enums import ProductId


@pytest.fixture
def dummy_device():
    class DummyDevice(SurepyDevice):
        def __init__(self, data, product=ProductId.HUB):
            self._product = product
            super().__init__(data)

        @property
        def product(self) -> ProductId:
            return self._product

    return DummyDevice


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


@pytest.mark.parametrize(
    "product",
    [ProductId.HUB, ProductId.PET_DOOR, ProductId.FEEDER_CONNECT],
)
def test_surepydevice_properties(dummy_device, product):
    """Test SurepyDevice property accessors."""
    data = make_data()
    device = dummy_device(data, product=product)
    assert device.id == 123
    assert device.household_id == 456
    assert device.name == "Test Device"
    assert device.available is True
    assert device.product_id == product.value
    assert device.product_name == product.name
    assert device.raw_data["id"] == 123
    assert str(device).startswith("<DummyDevice id=123>")


@pytest.mark.parametrize("battery,expected", [
    (6.4, 100),
    (1.2, 0),
    (3.8, 0),  # main code returns 0 for anything less than 6.4V
])
def test_battery_level(dummy_device, battery, expected):
    """Test battery_level calculation for various voltages."""
    device = dummy_device(make_data())
    device._data["status"]["battery"] = battery
    assert device.battery_level == expected


def test_surepydevice_notimplemented():
    class Dummy(SurepyDevice):
        @property
        def product(self):
            return ProductId.HUB

    d = Dummy({"id": 1, "household_id": 2, "name": "n"})
    with pytest.raises(NotImplementedError):
        d.refresh()

    class DummyNoProduct(SurepyDevice):
        pass

    with pytest.raises(TypeError):
        DummyNoProduct({"id": 1, "household_id": 2, "name": "n"})


def test_surepydevice_product_notimplemented():
    class Dummy(SurepyDevice):
        pass
    with pytest.raises(TypeError):
        Dummy({"id": 1, "household_id": 2, "name": "n"})


def test_surepydevice_str_and_parent():
    class Dummy(SurepyDevice):
        @property
        def product(self):
            return ProductId.HUB

    d = Dummy({"id": 1, "household_id": 2, "name": "n"})
    assert str(d) == "<Dummy id=1>"
    assert d.parent_device_id is None
    d2 = Dummy({"id": 2, "household_id": 2, "name": "n", "parent_device_id": 3})
    assert d2.parent_device_id == 3
