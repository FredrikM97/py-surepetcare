import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.devices.entities import BowlState
from surepcio.devices.feeder_connect import Bowls, BowlSetting, FeederConnect
from surepcio.enums import BowlPosition, BowlType, FoodType
from tests.conftest import object_snapshot


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["feeder_connect", "household"]])
async def test_snapshot(
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        devices = await client.api(household.get_devices())
        for device in devices:
            object_snapshot(device, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["feeder_connect", "household"]])
async def test_snapshot_set_bowls_command(
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
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
            object_snapshot(device, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["feeder_connect", "household"]])
async def test_snapshot_get_functions(
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        devices: list[FeederConnect] = await client.api(household.get_devices())

        for device in devices:
            results = {
                "fill_percentages": device.fill_percentages(),
                "get_bowl_type_option": device.get_bowl_type_option(),
            }
            object_snapshot(results, snapshot)


def test_fill_percentages_clamps_negative_and_preserves_none() -> None:
    device = FeederConnect({"id": 1, "household_id": 7777})
    device.status = device.statusCls(
        bowl_status=[
            BowlState(index=BowlPosition.ONE, current_weight=-5.0),
            BowlState(index=BowlPosition.TWO, current_weight=None),
            BowlState(index=BowlPosition.BOTH, current_weight=10.0),
        ]
    )
    device.control = device.controlCls(
        bowls=Bowls(
            settings=[
                BowlSetting(target=20.0),
                BowlSetting(target=20.0),
                BowlSetting(target=None),
            ]
        )
    )

    result = device.fill_percentages()

    assert result["per_bowl"] == {0: 0.0, 1: None, 2: None}
    assert result["total"] == 0.0


def test_fill_percentages_returns_none_when_no_data() -> None:
    device = FeederConnect({"id": 1, "household_id": 7777})

    result = device.fill_percentages()

    assert result == {"total": None, "per_bowl": {}}


def test_fill_percentages_returns_none_for_non_positive_targets() -> None:
    device = FeederConnect({"id": 1, "household_id": 7777})
    device.status = device.statusCls(
        bowl_status=[
            BowlState(index=BowlPosition.ONE, current_weight=10.0),
            BowlState(index=BowlPosition.TWO, current_weight=-5.0),
        ]
    )
    device.control = device.controlCls(
        bowls=Bowls(settings=[BowlSetting(target=0.0), BowlSetting(target=-10.0)])
    )

    result = device.fill_percentages()

    assert result["per_bowl"] == {0: None, 1: None}
    assert result["total"] is None
