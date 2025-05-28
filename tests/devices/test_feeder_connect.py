# Integration tests for FeederConnect device using mock data.
from surepetcare.devices.feeder_connect import FeederConnect
from surepetcare.enums import BowlPosition, FoodType, ProductId
from tests.mock_helpers import load_mock_data, MockSurePetcareClient

def test_feeder_connect_integration():
    client = MockSurePetcareClient({})
    feeder = FeederConnect(
        client, load_mock_data("tests/mock_data/mock_device_feeder_connect.json")['data'][0]
    )
    assert feeder.battery_level == 40
    assert feeder.id == 1
    assert feeder.household_id == 7777
    assert feeder.name == "Feeder 1"
    assert feeder.online is True
    assert feeder.product_id == 4
    assert feeder.product_id == ProductId.FEEDER_CONNECT
    assert feeder.lid_delay == 0
    assert feeder.bowls[BowlPosition.LEFT].food_type == FoodType.WET
    assert feeder.bowls[BowlPosition.RIGHT].food_type == FoodType.WET