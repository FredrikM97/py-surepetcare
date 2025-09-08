import pytest

from surepcio.devices.device import DeviceBase
from surepcio.enums import ProductId


def make_data():
    return {
        "id": 123,
        "household_id": 456,
        "name": "Test Device",
        "status": {"online": True, "battery": 6.0},
    }


def test_deviceBase_notimplemented():
    class Dummy(DeviceBase):
        @property
        def product(self):
            return ProductId.HUB

    d = Dummy({"product_id": 1, "household_id": 2, "name": "dummyName", "id": 1})
    with pytest.raises(NotImplementedError):
        d.refresh()

    class DummyNoProduct(DeviceBase):
        pass

    with pytest.raises(TypeError):
        DummyNoProduct()


def test_device_product_notimplemented():
    class Dummy(DeviceBase):
        pass

    with pytest.raises(TypeError):
        Dummy({"id": 1, "household_id": 2, "name": "n", "parent_device_id": 3, "product_id": 1})
