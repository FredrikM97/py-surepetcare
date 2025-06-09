import pytest

from surepetcare.devices import DEVICE_CLASS_REGISTRY
from surepetcare.devices import load_device_class
from surepetcare.enums import ProductId


def test_load_device_class_dynamic():
    dummy_class = type("DummyDevice", (), {})
    key = ProductId.PET
    original = DEVICE_CLASS_REGISTRY.get(key)
    DEVICE_CLASS_REGISTRY[key] = dummy_class
    try:
        result = load_device_class(ProductId.PET)
        assert result is dummy_class
    finally:
        if original is not None:
            DEVICE_CLASS_REGISTRY[key] = original
        else:
            del DEVICE_CLASS_REGISTRY[key]


def test_load_device_class_invalid():
    # Should return None for unknown ProductId
    class FakeProductId:
        pass

    assert load_device_class(9999) is None
    assert load_device_class(FakeProductId) is None


def test_load_device_class_none():
    # Should return None if ProductId.find returns None
    assert load_device_class(None) is None


# Test all registry keys for coverage
@pytest.mark.parametrize("product_id,expected_class", list(DEVICE_CLASS_REGISTRY.items()))
def test_load_device_class_registry_coverage(product_id, expected_class):
    assert load_device_class(product_id) is expected_class
