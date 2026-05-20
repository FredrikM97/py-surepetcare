import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import DevicePetTag
from surepcio.devices.pet import Pet
from surepcio.enums import ModifyDeviceTag
from surepcio.enums import PetDeviceLocationProfile
from surepcio.enums import PetLocation
from surepcio.security.exceptions import ApiError
from tests.conftest import object_snapshot


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "household"]])
async def test_snapshot(
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())
        for pet in pets:
            await client.api(pet.refresh())
            object_snapshot(pet, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "household"]])
async def test_set_position_command(register_device_api_mocks, mock_devices):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())

        for pet in pets:
            await client.api(pet.refresh())
            cmd = pet.set_position(PetLocation.INSIDE)

            assert cmd.method == "POST"
            assert cmd.endpoint.endswith(f"/pet/{pet.id}/position")
            assert "/async" not in cmd.endpoint
            assert cmd.params["where"] == PetLocation.INSIDE.value
            assert cmd.params["since"]
            response = await client.api(cmd)
            assert response["data"] == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "household"]])
async def test_set_profile_for_assigned_device_uses_client_put(
    register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())

        for pet in pets:
            pet.status.devices.items = [DevicePetTag(id=269654)]
            cmd = pet.set_profile(269654, PetDeviceLocationProfile.INDOOR_ONLY)

            assert cmd.method == "PUT"
            assert cmd.endpoint.endswith(f"/device/269654/tag/{pet.tag}/async")
            assert cmd.params == {"profile": PetDeviceLocationProfile.INDOOR_ONLY.value}
            await client.api(cmd)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "household"]])
async def test_set_profile_for_unassigned_device_raises_value_error(
    register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())

        for pet in pets:
            pet.status.devices.items = [DevicePetTag(id=269654)]

            with pytest.raises(ValueError, match="Device ID 271836"):
                pet.set_profile(271836, PetDeviceLocationProfile.NO_RESTRICTION)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "household"]])
async def test_set_tag_add_uses_client_put(register_device_api_mocks, mock_devices):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())

        for pet in pets:
            cmd = pet.set_tag(269654, ModifyDeviceTag.ADD)

            assert cmd.method == "PUT"
            assert cmd.endpoint.endswith(f"/device/269654/tag/{pet.tag}/async")
            await client.api(cmd)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "household"]])
async def test_fetch_assigned_devices_raises_on_forbidden(
    register_device_api_mocks, add_api_json_response, mock_devices
):
    """A 403 Forbidden response is returned by the API when the pet has no assigned device."""
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())

        for pet in pets:
            add_api_json_response(
                method="GET",
                endpoint=f"{API_ENDPOINT_PRODUCTION}/tag/{pet.tag}/device",
                payload={"error": "Forbidden"},
                status=403,
                overwrite=True,
            )
            cmd: Command = pet.fetch_assigned_devices()

            with pytest.raises(ApiError) as exc_info:
                await client.api(cmd)

            assert exc_info.value.status == 403
