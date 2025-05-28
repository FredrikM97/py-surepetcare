# Test for dynamic device class loading.
from surepetcare.helper import load_device_class


def test_load_device_class_dynamic():
    class DummyEnum:
        name = "DUMMY_DEVICE"

    import types

    dummy_module = types.ModuleType("surepetcare.devices.dummy_device")
    dummy_class = type("DummyDevice", (), {})
    setattr(dummy_module, "DummyDevice", dummy_class)
    import sys

    sys.modules["surepetcare.devices.dummy_device"] = dummy_module
    result = load_device_class(DummyEnum)
    assert result is dummy_class
