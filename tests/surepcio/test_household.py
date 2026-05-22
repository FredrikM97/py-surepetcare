import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.command import Command
from surepcio.devices.entities import DevicePetTag, SurePetcareResponse
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.devices.hub import Hub
from surepcio.devices.pet import Pet
from surepcio.enums import ProductId
from surepcio.security.exceptions import NotLoadedError, UnexpectedDataTypeError
from tests.conftest import object_snapshot


# --- Parametrized error/corner case tests ---
def test_get_pets_none_and_invalid_response() -> None:
    """get_pets chain raises on missing or wrongly-typed data."""
    household = Household({"id": 1, "timezone": {"timezone": "Europe/Stockholm"}})
    command: Command = household.get_pets()
    assert command.chain is not None
    with pytest.raises(NotLoadedError):
        command.chain(SurePetcareResponse(data=None))
    with pytest.raises(UnexpectedDataTypeError):
        command.chain(SurePetcareResponse(data={"data": {"not": "a list"}}))


def test_get_devices_none_and_invalid_response() -> None:
    """get_devices chain raises on missing or wrongly-typed data."""
    household = Household({"id": 1, "timezone": {"timezone": "Europe/Stockholm"}})
    command: Command = household.get_devices()
    assert command.chain is not None
    with pytest.raises(NotLoadedError):
        command.chain(SurePetcareResponse(data=None))
    with pytest.raises(UnexpectedDataTypeError):
        command.chain(SurePetcareResponse(data={"data": {"not": "a list"}}))


def test_get_households_none_and_invalid_response() -> None:
    """get_households parse raises on missing or wrongly-typed data."""
    command: Command = Household.get_households()
    assert command.parse is not None
    with pytest.raises(NotLoadedError):
        command.parse(SurePetcareResponse(data=None))
    with pytest.raises(UnexpectedDataTypeError):
        command.parse(SurePetcareResponse(data={"data": {"not": "a list"}}))


def test_get_household_and_product_none_and_invalid() -> None:
    """get_household and get_product parse raise on missing or wrongly-typed data."""
    for command in (
        Household.get_household(1),
        Household.get_product(ProductId.FEEDER_CONNECT, 2),
    ):
        assert command.parse is not None
        with pytest.raises(NotLoadedError):
            command.parse(SurePetcareResponse(data=None))
        with pytest.raises(UnexpectedDataTypeError):
            command.parse(SurePetcareResponse(data={"data": [1, 2, 3]}))


def test_get_devices_skips_invalid_product() -> None:
    """get_devices chain silently skips product_ids not in the ProductId enum."""
    mock_data = SurePetcareResponse(
        data={
            "data": [
                {"id": 10, "household_id": 1, "name": "Hub1", "product_id": 999, "status": {"online": True}},
                {"id": 11, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}},
            ]
        }
    )
    household = Household({"id": 1, "timezone": {"timezone": "Europe/Stockholm"}})
    command: Command = household.get_devices()
    assert command.chain is not None
    command.chain(mock_data)
    devices: list = household.data["devices"]
    assert len(devices) == 1
    assert devices[0].id == 11


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["household"]])
async def test_get_pets_empty_household(
    add_api_json_response, register_device_api_mocks, mock_devices
) -> None:
    """get_pets returns [] and does not crash when the API returns no pets."""
    register_device_api_mocks(mock_devices)
    add_api_json_response("GET", "/api/pet", {"data": []}, match_querystring=False)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())

    assert pets == []
    assert household.data["pets"] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["household"]])
async def test_snapshot(snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices) -> None:
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: list[Household] = await client.api(Household.get_households())
        object_snapshot(household, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["household", "product"]])
async def test_get_product(snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices) -> None:
    """Test fetching a product for a device using aresponses and household fixture."""
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        command: Command = Household.get_product(ProductId.FEEDER_CONNECT, 2)
        result = await client.api(command)
        assert "bowls" in result
        assert result["bowls"]["type"] == 4
        object_snapshot(result, snapshot)


def test_fetch_pet_device_assignments_requires_both_loaded() -> None:
    """Raises NotLoadedError if pets or devices have not been loaded yet."""
    h_no_pets = Household({"id": 1})
    h_no_pets.data["devices"] = []
    with pytest.raises(NotLoadedError, match="Pets have not been loaded"):
        h_no_pets.fetch_pet_device_assignments()

    h_no_devices = Household({"id": 1})
    h_no_devices.data["pets"] = []
    with pytest.raises(NotLoadedError, match="Devices have not been loaded"):
        h_no_devices.fetch_pet_device_assignments()


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "feeder_connect_without_tags", "household"]])
async def test_fetch_pet_device_assignments(register_device_api_mocks, mock_devices) -> None:
    """fetch_pet_device_assignments refreshes devices, then maps pets to matched device tags.

    Pet "Maui" (tag.id=60978) matches feeder device 269654 (tags[0].id=60978).
    Pet "Fionna" (tag.id=1725049) has no match and is excluded.
    """
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())
        devices: list[FeederConnect | Hub] = await client.api(household.get_devices())

        matched_tag_ids: set[int] = {
            tag.id
            for device in devices
            if device.control.tags
            for tag in device.control.tags
            if tag.id is not None
        }
        matched_pets: list[Pet] = [p for p in pets if p.tag in matched_tag_ids]
        excluded_pets: list[Pet] = [p for p in pets if p.tag not in matched_tag_ids]

        assert len(excluded_pets) > 0, "Expected at least one excluded pet — check fixture tags"
        assert 0 < len(matched_pets) < len(pets)

        for pet in excluded_pets:
            pet.status.devices.items = [DevicePetTag(id=999)]
            pet.status.devices.count = 1

        commands: list[Command] = household.fetch_pet_device_assignments()
        assert len(commands) == len(matched_pets)
        await client.api(commands)

    for pet in excluded_pets:
        assert pet.status.devices.items == []
        assert pet.status.devices.count == 0
