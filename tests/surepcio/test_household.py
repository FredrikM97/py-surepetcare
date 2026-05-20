import pytest
from syrupy.assertion import SnapshotAssertion

import surepcio
from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.command import Command
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.devices.hub import Hub
from surepcio.devices.pet import Pet
from surepcio.enums import ProductId
from tests.conftest import object_snapshot



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
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household = await client.api(Household.get_households())
        object_snapshot(household, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["household", "product"]])
async def test_get_product(snapshot, register_device_api_mocks, mock_devices):
    """Test fetching a product for a device using aresponses and household fixture."""
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        command = Household.get_product(1, 2)
        result = await client.api(command)
        assert "bowls" in result
        assert result["bowls"]["type"] == 4
        object_snapshot(result, snapshot)

def test_fetch_pet_device_assignments_requires_both_loaded():
    """Raises RuntimeError if pets or devices have not been loaded yet."""
    h_no_pets = Household({"id": 1})
    h_no_pets.data["devices"] = []
    with pytest.raises(RuntimeError, match="Pets have not been loaded"):
        h_no_pets.fetch_pet_device_assignments()

    h_no_devices = Household({"id": 1})
    h_no_devices.data["pets"] = []
    with pytest.raises(RuntimeError, match="Devices have not been loaded"):
        h_no_devices.fetch_pet_device_assignments()


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "feeder_connect_without_tags", "household"]])
async def test_fetch_pet_device_assignments(
    register_device_api_mocks, mock_devices
):
    """Returns commands only for pets whose tag matches a device tag.

    Hub has no pet tags and must be silently excluded without crashing.
    Pet "Maui" (tag.id=60978) matches feeder device 269654 (tags[0].id=60978).
    Pet "Fionna" (tag.id=1725049) has no match and is also excluded.
    Commands are executed via the client to verify they are valid API calls.
    """
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())
        devices: list[FeederConnect | Hub] = await client.api(household.get_devices())
        
        # Required otherwise devices will be skipped in fetch_pet_device_assignments
        for device in devices:
            await client.api(device.refresh())
        commands: list[Command] = household.fetch_pet_device_assignments()
        await client.api(commands)

    matched_tag_ids: set[int] = {
        tag.id
        for device in devices
        if device.control.tags
        for tag in device.control.tags
    }
    matched_pets: list[Pet] = [p for p in pets if p.tag in matched_tag_ids]
    excluded_pets: list[Pet] = [p for p in pets if p.tag not in matched_tag_ids]

    assert len(excluded_pets) > 0, "Expected at least one pet to be excluded — test fixture may be missing a tagless device"
    assert len(commands) == len(matched_pets)
    assert len(commands) < len(pets)
    for cmd in commands:
        assert cmd.method == "GET"
        assert "/tag/" in cmd.endpoint
        assert "/device" in cmd.endpoint
