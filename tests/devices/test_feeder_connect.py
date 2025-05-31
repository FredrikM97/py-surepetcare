# Integration tests for FeederConnect device using mock data.
import pytest

from surepetcare.const import API_ENDPOINT_V1
from surepetcare.devices.feeder_connect import FeederConnect
from surepetcare.enums import BowlPosition
from surepetcare.enums import FoodType
from surepetcare.enums import ProductId
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import MockSurePetcareClient


def test_feeder_connect_integration():
    feeder = FeederConnect(load_mock_data("tests/mock_data/mock_device_feeder_connect.json")["data"][0])
    assert feeder.battery_level == 40
    assert feeder.id == 1
    assert feeder.household_id == 7777
    assert feeder.name == "Feeder 1"
    assert feeder.available is True
    assert feeder.product_id == 4
    assert feeder.product_id == ProductId.FEEDER_CONNECT
    assert feeder.lid_delay == 0
    assert feeder.bowls[BowlPosition.LEFT].food_type == FoodType.WET
    assert feeder.bowls[BowlPosition.RIGHT].food_type == FoodType.WET


@pytest.mark.asyncio
async def test_feeder_connect_refresh():
    mock_data = {
        "data": {
            "id": 1,
            "household_id": 1,
            "name": "Feeder1",
            "product_id": 4,
            "status": {"online": True},
            "control": {
                "lid": {"close_delay": 5},
                "bowls": {"settings": [{"food_type": 1}, {"food_type": 2}]},
            },
        }
    }
    client = MockSurePetcareClient({f"{API_ENDPOINT_V1}/device/1": mock_data})
    feeder = FeederConnect(
        {
            "id": 1,
            "household_id": 1,
            "name": "Feeder1",
            "product_id": 4,
            "status": {"online": True},
            "control": {
                "lid": {"close_delay": 5},
                "bowls": {"settings": [{"food_type": 1}, {"food_type": 2}]},
            },
        }
    )
    command = feeder.refresh()
    result = await client.api(command)
    assert result is feeder
    assert feeder._data["name"] == "Feeder1"
    assert feeder.lid_delay == 5
    assert len(feeder.bowls) == 2
