import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio.devices.feeder_connect import Bowls
from surepcio.devices.feeder_connect import BowlSetting
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.enums import BowlType
from surepcio.enums import FoodType
from surepcio import Household
from tests.mock_helpers import MockClient
from tests.mock_helpers import recursive_dump


@pytest.fixture
def device_file():
    return "tests/fixture/feeder_connect.json"


@pytest.fixture
def device_control_file():
    return "tests/fixture/feeder_connect_control.json"


@pytest.fixture
def household_file():
    return "tests/fixture/household.json"


@pytest.mark.asyncio
async def test_snapshot(snapshot: SnapshotAssertion, household_file, device_file):
    snapshot.snapshot_dir = "tests/snapshots"
    client = MockClient(fixture_file=device_file)
    client.set_mock_response(household_file)
    household = await client.api(Household.get_household(7777))
    client.reset()
    devices = await client.api(household.get_devices())
    for device in devices:
        await client.api(device.refresh())
        data = recursive_dump(device)
        assert data == snapshot


async def test_snapshot_set_bowls_command(snapshot: SnapshotAssertion, household_file, device_control_file):
    snapshot.snapshot_dir = "tests/snapshots"
    client = MockClient(fixture_file=device_control_file, use_method="set_bowls")
    client.set_mock_response(household_file)
    household = await client.api(Household.get_household(7777))
    client.reset()
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
        data = recursive_dump(device)
        assert data == snapshot
