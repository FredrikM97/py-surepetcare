from surepetcare.devices import DEVICE_CLASS_REGISTRY
from surepetcare.devices import load_device_class
from surepetcare.enums import ProductId


def test_load_device_class_dynamic():
    dummy_class = type("DummyDevice", (), {})
    # Use a real ProductId for testing (e.g., ProductId.PET)
    key = ProductId.PET
    original = DEVICE_CLASS_REGISTRY.get(key)
    DEVICE_CLASS_REGISTRY[key] = dummy_class
    try:
        result = load_device_class(ProductId.PET)
        assert result is dummy_class
    finally:
        # Restore original value
        if original is not None:
            DEVICE_CLASS_REGISTRY[key] = original
        else:
            del DEVICE_CLASS_REGISTRY[key]
