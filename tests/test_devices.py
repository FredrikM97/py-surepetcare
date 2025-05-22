import pytest
from surepy.devices.feeder_connect import FeederConnect
from surepy.devices.hub import Hub
from surepy.entities.pet import Pet
from surepy.enums import BowlPosition, FoodType, ProductId
from tests.mock_helpers import MockSurePetcareClient, load_mock_data


def test_feeder_connect():
    client = MockSurePetcareClient({})
    # We only load the first pet
    feeder = FeederConnect(client,load_mock_data("tests/mock_data/mock_device_feeder_connect.json")['data'][0])
    assert feeder.battery_level == 47
    assert feeder.id == 269654
    assert feeder.household_id == 7777
    assert feeder.name == "Cat feeder"
    assert feeder.online is False
    assert feeder.product_id == 4
    assert feeder.product_id == ProductId.FEEDER_CONNECT
    assert feeder.lid_delay == 4
    assert feeder.bowls[BowlPosition.LEFT].food_type == FoodType.DRY
    assert feeder.bowls[BowlPosition.RIGHT].food_type == FoodType.DRY


def test_hub():
    client = MockSurePetcareClient({})
    # We only load the first pet
    hub = Hub(client,load_mock_data("tests/mock_data/mock_device_hub.json")['data'][0])
    assert hub.household_id == 7777
    assert hub.id == 295972
    assert hub.name == "Hem-hub"
    assert hub.product_id == 1
    assert hub.product_id == ProductId.HUB
    assert hub.online is True
    assert hub.battery_level == None
