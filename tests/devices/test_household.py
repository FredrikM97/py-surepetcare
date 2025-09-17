import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from tests.mock_helpers import MockClient
from tests.mock_helpers import recursive_dump


@pytest.fixture
def household_file():
    return "tests/fixture/household.json"


@pytest.mark.asyncio
async def test_snapshot(snapshot: SnapshotAssertion, household_file):
    snapshot.snapshot_dir = "tests/snapshots"
    client = MockClient(fixture_file=household_file)
    household = await client.api(Household.get_households())
    assert recursive_dump(household) == snapshot
