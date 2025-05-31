import pytest

from surepetcare.client import SurePetcareClient
from surepetcare.const import API_ENDPOINT_V1
from surepetcare.const import API_ENDPOINT_V2
from surepetcare.household import Household
from tests.mock_helpers import MockSurePetcareClient


@pytest.mark.asyncio
async def test_get_households(monkeypatch):
    # Mock API response
    async def mock_get(endpoint, params=None):
        return {"data": [{"id": 1}, {"id": 2}]}

    client = SurePetcareClient()
    monkeypatch.setattr(client, "get", mock_get)
    command = Household.get_households()
    result = await client.api(command)
    assert isinstance(result, list)
    assert result[0].id == 1
    assert result[1].id == 2


@pytest.mark.asyncio
async def test_get_household():
    mock_data = {"id": 1, "name": "TestHouse"}
    endpoint = f"{API_ENDPOINT_V1}/household/1"
    client = MockSurePetcareClient({endpoint: mock_data})
    command = Household.get_household(1)
    result = await client.api(command)
    assert (isinstance(result, dict) and result["id"] == 1) or (hasattr(result, "id") and result.id == 1)


@pytest.mark.asyncio
async def test_get_pets():
    mock_data = {
        "data": [
            {"id": 1, "household_id": 1, "name": "Pet1", "tag": {"id": "A1"}},
            {"id": 2, "household_id": 1, "name": "Pet2", "tag": {"id": "B2"}},
        ]
    }
    client = MockSurePetcareClient({f"{API_ENDPOINT_V1}/pet": mock_data})
    household = Household({"id": 1})
    command = household.get_pets()
    pets = await client.api(command)
    assert len(pets) == 2
    assert pets[0].id == 1
    assert pets[1].id == 2


@pytest.mark.asyncio
async def test_get_devices():
    mock_data = {
        "data": [
            {"id": 10, "household_id": 1, "name": "Hub1", "product_id": 1, "status": {"online": True}},
            {"id": 11, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}},
        ]
    }
    client = MockSurePetcareClient({f"{API_ENDPOINT_V1}/device": mock_data})
    household = Household({"id": 1})
    command = household.get_devices()
    devices = await client.api(command)
    assert len(devices) == 2
    assert devices[0].id == 10
    assert devices[1].id == 11


@pytest.mark.asyncio
async def test_get_product():
    mock_data = {"foo": "bar"}
    endpoint = f"{API_ENDPOINT_V2}/product/1/device/2/control"
    client = MockSurePetcareClient({endpoint: mock_data})
    command = Household.get_product(1, 2)
    result = await client.api(command)
    assert result == {"foo": "bar"}
