# Integration tests for FeederConnect device using mock data.
import pytest

from surepetcare.const import API_ENDPOINT_V1
from surepetcare.devices.feeder_connect import FeederConnect
from surepetcare.enums import FoodType
from surepetcare.enums import ProductId
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import MockSurePetcareClient


def test_feeder_connect_integration():
    # Ensure mock data includes all required fields for BowlState
    data = load_mock_data("tests/mock_data/mock_device_feeder_connect.json")
    # Patch: ensure 'bowl_status' is present in status after refresh
    data["data"][0]["status"]["bowl_status"] = [
        {"index": 0, "food_type": 1, "substance_type": 0, "current_weight": 0.0, "last_filled_at": "", "last_zeroed_at": "", "fill_percent": 0},
        {"index": 1, "food_type": 1, "substance_type": 0, "current_weight": 0.0, "last_filled_at": "", "last_zeroed_at": "", "fill_percent": 0}
    ]
    for bowl in data["data"][0]["control"]["bowls"]["settings"]:
        bowl.setdefault("substance_type", 0)
        bowl.setdefault("current_weight", 0.0)
        bowl.setdefault("last_filled_at", "")
        bowl.setdefault("last_zeroed_at", "")
        bowl.setdefault("fill_percent", 0)
    feeder = FeederConnect(data["data"][0])
    assert feeder.battery_level == 40
    assert feeder.id == 1
    assert feeder.household_id == 7777
    assert feeder.name == "Feeder 1"
    assert feeder.available is True
    assert feeder.product_id == 4
    assert feeder.product_id == ProductId.FEEDER_CONNECT
    assert feeder.lid_delay == 0
    # Use bowls property (which is bowl_status) for backward compatibility
    assert len(feeder.bowls) == 2
    assert feeder.bowls[0].food_type == FoodType.WET
    assert feeder.bowls[1].food_type == FoodType.WET


@pytest.mark.asyncio
async def test_feeder_connect_refresh():
    # The refreshed data must include 'bowl_status' in 'status' for feeder.bowls to work
    refreshed_data = {
        "id": 1,
        "household_id": 1,
        "name": "Feeder1",
        "product_id": 4,
        "status": {"online": True, "bowl_status": [
            {"index": 0, "food_type": 1, "substance_type": 0, "current_weight": 0.0, "last_filled_at": "", "last_zeroed_at": "", "fill_percent": 0},
            {"index": 1, "food_type": 1, "substance_type": 0, "current_weight": 0.0, "last_filled_at": "", "last_zeroed_at": "", "fill_percent": 0}
        ]},
        "control": {
            "lid": {"close_delay": 5},
            "bowls": {"settings": [
                {"food_type": 1, "substance_type": 0, "current_weight": 0.0, "last_filled_at": "", "last_zeroed_at": "", "fill_percent": 0},
                {"food_type": 1, "substance_type": 0, "current_weight": 0.0, "last_filled_at": "", "last_zeroed_at": "", "fill_percent": 0}
            ]},
        },
    }
    # The client must return {'data': refreshed_data} for the endpoint
    client = MockSurePetcareClient({f"{API_ENDPOINT_V1}/device/1": {"data": refreshed_data}})
    # The initial feeder data can be anything, since it will be replaced by the refresh
    feeder = FeederConnect({"id": 1, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}, "control": {"lid": {"close_delay": 5}, "bowls": {"settings": []}}})
    command = feeder.refresh()
    result = await client.api(command)
    assert result is feeder
    assert feeder._data["name"] == "Feeder1"
    assert feeder.lid_delay == 5
    # Use bowls property (which is bowl_status) for backward compatibility
    assert len(feeder.bowls) == 2
    assert feeder.bowls[0].food_type == FoodType.WET
    assert feeder.bowls[1].food_type == FoodType.WET
