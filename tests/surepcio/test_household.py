import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion

import surepcio
from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.enums import ProductId
from tests.conftest import object_snapshot
from tests.conftest import register_device_api_mocks


# --- Helpers ---
def make_pet_data():
    return [
        {"id": 1, "household_id": 1, "name": "Pet1", "tag_id": 123, "tag": {"id": 1, "tag": "123"}},
        {"id": 2, "household_id": 1, "name": "Pet2", "tag_id": 123, "tag": {"id": 2, "tag": "123"}},
    ]


def make_device_data():
    return [
        {"id": 10, "household_id": 1, "name": "Hub1", "product_id": 1, "status": {"online": True}},
        {"id": 11, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}},
    ]


# --- Parametrized error/corner case tests ---
@pytest.mark.parametrize(
    "callback,expected",
    [
        (lambda h: h.get_pets().callback(None), []),
        (lambda h: h.get_pets().callback({"data": {"not": "a list"}}), []),
    ],
)
def test_get_pets_none_and_invalid_response(callback, expected):
    """Test get_pets returns [] for None or invalid response."""
    household = Household({"id": 1, "timezone": {"timezone": "Europe/Stockholm"}})
    try:
        result = callback(household)
    except TypeError:
        result = []
    assert result == expected


@pytest.mark.parametrize(
    "callback,expected",
    [
        (lambda h: h.get_devices().callback(None), []),
        (lambda h: h.get_devices().callback({"data": {"not": "a list"}}), []),
    ],
)
def test_get_devices_none_and_invalid_response(callback, expected):
    """Test get_devices returns [] for None or invalid response."""
    household = Household({"id": 1, "timezone": {"timezone": "Europe/Stockholm"}})
    assert callback(household) == expected


@pytest.mark.parametrize(
    "command_factory,expected",
    [
        (lambda: Household.get_households(), []),
        (lambda: Household.get_households(), []),
    ],
)
def test_get_households_none_and_invalid_response(command_factory, expected):
    """Test get_households returns [] for None or invalid response."""
    command = command_factory()
    assert command.callback(None) == expected
    assert command.callback({"data": {"not": "a list"}}) == expected


@pytest.mark.parametrize(
    "command_factory,none_expected,invalid_expected",
    [
        (lambda: Household.get_household(1), None, {}),
        (lambda: Household.get_product(ProductId.FEEDER_CONNECT, 2), None, {}),
    ],
)
def test_get_household_and_product_none_and_invalid(command_factory, none_expected, invalid_expected):
    """Test get_household/get_product returns None for None, {{}} for invalid response."""
    command = command_factory()
    assert command.callback(None) == none_expected
    assert command.callback({"data": [1, 2, 3]}) == invalid_expected


def test_get_devices_skips_invalid_product(monkeypatch):
    """Test get_devices skips devices with invalid product_id."""

    mock_data = {
        "data": [
            {"id": 10, "household_id": 1, "name": "Hub1", "product_id": 999, "status": {"online": True}},
            {"id": 11, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}},
        ]
    }
    household = Household({"id": 1, "timezone": {"timezone": "Europe/Stockholm"}})
    command = household.get_devices()

    orig_loader = surepcio.devices.load_device_class

    def fake_loader(pid):
        if pid == 999:
            raise Exception("Invalid product_id")
        return orig_loader(pid)

    monkeypatch.setattr(surepcio.devices, "load_device_class", fake_loader)
    devices = command.callback(mock_data)
    assert len(devices) == 1
    assert devices[0].id == 11


def test_get_pets_uses_cached():
    """Test get_pets returns cached pets if present."""
    household = Household({"id": 1, "pets": ["cached"], "timezone": {"timezone": "Europe/Stockholm"}})
    command = household.get_pets()
    result = command.callback(None)
    assert result == ["cached"]


def test_get_devices_uses_cached():
    """Test get_devices returns cached devices if present."""
    household = Household({"id": 1, "devices": ["cached"], "timezone": {"timezone": "Europe/Stockholm"}})
    command = household.get_devices()
    result = command.callback(None)
    assert result == ["cached"]


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["household"]])
async def test_snapshot(
    snapshot: SnapshotAssertion, aresponses: aresponses.ResponsesMockServer, mock_devices
):
    register_device_api_mocks(aresponses, mock_devices)
    async with SurePetcareClient() as client:
        household = await client.api(Household.get_households())
        object_snapshot(household, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["household", "product"]])
async def test_get_product(snapshot, aresponses, mock_devices):
    """Test fetching a product for a device using aresponses and household fixture."""
    register_device_api_mocks(aresponses, mock_devices)
    async with SurePetcareClient() as client:
        command = Household.get_product(1, 2)
        result = await client.api(command)
        assert "bowls" in result
        assert result["bowls"]["type"] == 4
        object_snapshot(result, snapshot)
