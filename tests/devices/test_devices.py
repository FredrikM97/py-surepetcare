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

    d = Dummy()
    with pytest.raises(NotImplementedError):
        d.refresh()

    class DummyNoProduct(SurepyDevice):
        pass

    with pytest.raises(TypeError):
        DummyNoProduct()


def test_surepydevice_product_notimplemented():
    class Dummy(SurepyDevice):
        pass

    with pytest.raises(TypeError):
        Dummy({"id": 1, "household_id": 2, "name": "n", "parent_device_id": 3, "product_id": 1})
