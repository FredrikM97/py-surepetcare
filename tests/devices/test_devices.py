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


def test_surepydevice_notimplemented():
    class Dummy(SurepyDevice):
        @property
        def product(self):
            return ProductId.HUB

    d = Dummy({"id": 1, "household_id": 2, "name": "n", "product_id": 1, "parent_device_id": 3})
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
        Dummy({"id": 1, "household_id": 2, "name": "n", "parent_device_id": 3, "product_id": 1})


def test_surepydevice_str_and_parent():
    class Dummy(SurepyDevice):
        @property
        def product(self):
            return ProductId.HUB

    d = Dummy({"id": 1, "household_id": 2, "name": "n", "product_id": 1, "parent_device_id": 5})
    assert str(d) == "<Dummy id=1>"
    assert d.parent_device_id == 5
    d2 = Dummy({"id": 2, "household_id": 2, "name": "n", "parent_device_id": 3, "product_id": 1})
    assert d2.parent_device_id == 3
