import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from tests.conftest import object_snapshot
from tests.conftest import register_device_api_mocks


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet_door", "household"]])
async def test_snapshot(
    snapshot: SnapshotAssertion, aresponses: aresponses.ResponsesMockServer, mock_devices
):
    register_device_api_mocks(aresponses, mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        devices = await client.api(household.get_devices())
        for device in devices:
            await client.api(device.refresh())
            assert object_snapshot(device, snapshot)
