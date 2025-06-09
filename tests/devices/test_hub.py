# Integration tests for Hub device using mock data.
from surepetcare.devices.hub import Hub
from surepetcare.enums import ProductId
from tests.mock_helpers import load_mock_data


def make_hub():
    return Hub(load_mock_data("tests/mock_data/mock_device_hub.json")["data"][0])


def test_hub_integration():
    """Test Hub device properties from mock data."""
    hub = make_hub()
    assert hub.household_id == 7777
    assert hub.id == 295972
    assert hub.name == "Hem-hub"
    assert hub.product_id == 1
    assert hub.product_id == ProductId.HUB
    assert hub.available is True
    assert hub.battery_level is None


def test_hub_missing_fields():
    """Test Hub with missing status and battery fields."""
    data = {"id": 1, "household_id": 2, "name": "HubNoStatus"}
    hub = Hub(data)
    assert hub.available is None
    assert hub.battery_level is None
