import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.devices.feeder_connect import Bowls
from surepcio.devices.feeder_connect import BowlSetting
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.enums import BowlType
from surepcio.enums import FoodType
from tests.conftest import object_snapshot
from tests.conftest import register_device_api_mocks


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["feeder_connect", "household"]])
async def test_snapshot(
    snapshot: SnapshotAssertion, aresponses: aresponses.ResponsesMockServer, mock_devices
):
    register_device_api_mocks(aresponses, mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        devices = await client.api(household.get_devices())
        for device in devices:
            await client.api(device.refresh())
            object_snapshot(device, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["feeder_connect", "household"]])
async def test_snapshot_set_bowls_command(
    snapshot: SnapshotAssertion, aresponses: aresponses.ResponsesMockServer, mock_devices
):
    register_device_api_mocks(aresponses, mock_devices)
    async with SurePetcareClient() as client:
        household = await client.api(Household.get_household(7777))
        devices: list[FeederConnect] = await client.api(household.get_devices())

        for device in devices:
            cmd = device.set_bowls(
                Bowls(
                    settings=[
                        BowlSetting(food_type=FoodType.WET, target=50),
                        BowlSetting(food_type=FoodType.WET, target=100),
                    ],
                    type=BowlType.TWO_SMALL,
                )
            )
            assert cmd.method == "PUT"
            await client.api(cmd)
            assert device.controlCls(**cmd.params).bowls == device.control.bowls
            object_snapshot(device, snapshot)
