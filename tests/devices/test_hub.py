# Integration tests for Hub device using mock data.
from surepetcare.devices.hub import Hub
from surepetcare.enums import ProductId
from tests.mock_helpers import load_mock_data, MockSurePetcareClient

def test_hub_integration():
    client = MockSurePetcareClient({})
    hub = Hub(client, load_mock_data("tests/mock_data/mock_device_hub.json")['data'][0])
    assert hub.household_id == 7777
    assert hub.id == 295972
    assert hub.name == "Hem-hub"
    assert hub.product_id == 1
    assert hub.product_id == ProductId.HUB
    assert hub.online is True
    assert hub.battery_level is None