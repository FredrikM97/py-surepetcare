import pytest

from surepetcare.const import API_ENDPOINT_V2
from surepetcare.devices.pet import Pet
from surepetcare.devices.pet import ReportHouseholdDrinkingResource
from surepetcare.devices.pet import ReportHouseholdFeedingResource
from surepetcare.devices.pet import ReportHouseholdMovementResource
from surepetcare.devices.pet import ReportHouseholdResource
from surepetcare.devices.pet import ReportWeightFrame
from tests.mock_helpers import MockSurePetcareClient


@pytest.fixture
def pet():
    return Pet({"id": 2, "household_id": 1, "name": "N", "tag": {"id": 3}})


@pytest.mark.asyncio
async def test_pet_fetch_and_properties(pet):
    """Test fetch_report and pet properties."""
    client = MockSurePetcareClient(
        {
            f"{API_ENDPOINT_V2}/report/household/1/pet/2/aggregate": {
                "data": {"feeding": [], "movement": [], "drinking": []}
            }
        }
    )
    # event_type not in [1,2,3] should raise
    with pytest.raises(ValueError):
        pet.fetch_report("2024-01-01", "2024-01-02", event_type=99)
    # valid event_type
    command = pet.fetch_report("2024-01-01", "2024-01-02", event_type=1)
    await client.api(command)
    assert hasattr(pet, "_report")
    assert pet.feeding == []
    assert pet.movement == []
    assert pet.drinking == []


@pytest.mark.parametrize(
    "attr,expected",
    [
        ("id", 2),
        ("household_id", 1),
        ("name", "N"),
        ("tag", 3),
        ("product.name", "PET"),
    ],
)
def test_pet_properties(pet, attr, expected):
    """Test pet property values."""
    value = pet
    for part in attr.split("."):
        value = getattr(value, part)
    assert value == expected


@pytest.mark.asyncio
async def test_pet_get_pet_dashboard():
    endpoint = f"{API_ENDPOINT_V2}/dashboard/pet"
    # Now, the mock should return an empty dict to simulate 'not response'
    client = MockSurePetcareClient({endpoint: {}})
    pet = Pet({"id": 1, "household_id": 2, "name": "N", "tag": {"id": 3}})
    command = pet.get_pet_dashboard("2024-01-01", [1])
    result = await client.api(command)
    assert result == []


@pytest.mark.asyncio
async def test_pet_refresh(pet):
    client = MockSurePetcareClient(
        {
            f"{API_ENDPOINT_V2}/report/household/1/pet/2/aggregate": {
                "data": {"feeding": [], "movement": [], "drinking": []}
            }
        }
    )
    command = pet.fetch_report("2024-01-01", "2024-01-02", event_type=1)
    await client.api(command)
    refreshed = pet.refresh()
    # refresh() returns a Command, so execute it
    await client.api(refreshed)
    assert hasattr(pet, "_report")


def test_report_household_movement_resource_flatten():
    # Test flatten_data with 'datapoints' key (should not error if 'data' is missing)
    data = {
        "datapoints": {},
        "created_at": "2024-01-01",
        "updated_at": "2024-01-01",
        "deleted_at": "2024-01-01",
        "device_id": 1,
        "tag_id": 2,
        "user_id": 3,
        "from": "A",
        "to": "B",
        "duration": 10,
        "entry_device_id": 1,
        "entry_user_id": 2,
        "exit_device_id": 3,
        "exit_user_id": 4,
        "active": True,
        "exit_movement_id": 5,
        "entry_movement_id": 6,
    }
    obj = ReportHouseholdMovementResource(**data)
    assert obj.device_id == 1
    assert obj.from_ == "A"


def test_report_household_feeding_resource_flatten():
    # Test flatten_data with 'data' key and weights as ints
    data = {
        "data": {
            "from": "2024-01-01",
            "to": "2024-01-02",
            "duration": 10,
            "context": 123,
            "bowl_count": 2,
            "device_id": 1,
            "weights": [1, 2],
            "actual_weight": 5.0,
            "entry_user_id": 1,
            "exit_user_id": 2,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01",
            "deleted_at": "2024-01-01",
            "tag_id": 1,
            "user_id": 2,
        }
    }
    obj = ReportHouseholdFeedingResource(**data)
    assert obj.context == "123"
    assert isinstance(obj.weights, list)
    # The weights list should contain ReportWeightFrame objects, not dicts
    assert all(isinstance(w, ReportWeightFrame) for w in obj.weights)
    # Also test with no 'data' key (direct dict)
    data2 = {
        "from": "2024-01-01",
        "to": "2024-01-02",
        "duration": 10,
        "context": 123,
        "bowl_count": 2,
        "device_id": 1,
        "weights": [1, 2],
        "actual_weight": 5.0,
        "entry_user_id": 1,
        "exit_user_id": 2,
        "created_at": "2024-01-01",
        "updated_at": "2024-01-01",
        "deleted_at": "2024-01-01",
        "tag_id": 1,
        "user_id": 2,
    }
    obj2 = ReportHouseholdFeedingResource(**data2)
    assert obj2.context == "123"
    assert isinstance(obj2.weights, list)
    assert all(isinstance(w, ReportWeightFrame) for w in obj2.weights)


def test_report_household_drinking_resource_flatten():
    # Test flatten_data with 'datapoints' key (should not error if 'data' is missing)
    data = {
        "datapoints": {},
        "from": "2024-01-01",
        "to": "2024-01-02",
        "duration": 10,
        "context": "ctx",
        "bowl_count": 2,
        "device_id": 1,
        "weights": [1.0, 2.0],
        "actual_weight": 5.0,
        "entry_user_id": 1,
        "exit_user_id": 2,
        "created_at": "2024-01-01",
        "updated_at": "2024-01-01",
        "deleted_at": "2024-01-01",
        "tag_id": 1,
        "user_id": 2,
    }
    obj = ReportHouseholdDrinkingResource(**data)
    assert obj.context == "ctx"
    assert obj.weights == [1.0, 2.0]


def test_report_household_resource_flatten_datapoints():
    # Test flatten_datapoints for movement, feeding, drinking
    data = {
        "pet_id": 1,
        "device_id": 2,
        "movement": {
            "datapoints": [
                {
                    "device_id": 1,
                    "tag_id": 2,
                    "user_id": 3,
                    "from": "A",
                    "to": "B",
                    "duration": 10,
                    "created_at": "2024-01-01",
                    "updated_at": "2024-01-01",
                    "deleted_at": "2024-01-01",
                    "entry_device_id": 1,
                    "entry_user_id": 2,
                    "exit_device_id": 3,
                    "exit_user_id": 4,
                    "active": True,
                    "exit_movement_id": 5,
                    "entry_movement_id": 6,
                }
            ]
        },
        "feeding": {
            "datapoints": [
                {
                    "from": "2024-01-01",
                    "to": "2024-01-02",
                    "duration": 10,
                    "context": "ctx",
                    "bowl_count": 2,
                    "device_id": 1,
                    "weights": [],
                    "actual_weight": 5.0,
                    "entry_user_id": 1,
                    "exit_user_id": 2,
                    "created_at": "2024-01-01",
                    "updated_at": "2024-01-01",
                    "deleted_at": "2024-01-01",
                    "tag_id": 1,
                    "user_id": 2,
                }
            ]
        },
        "drinking": {
            "datapoints": [
                {
                    "from": "2024-01-01",
                    "to": "2024-01-02",
                    "duration": 10,
                    "context": "ctx",
                    "bowl_count": 2,
                    "device_id": 1,
                    "weights": [1.0],
                    "actual_weight": 5.0,
                    "entry_user_id": 1,
                    "exit_user_id": 2,
                    "created_at": "2024-01-01",
                    "updated_at": "2024-01-01",
                    "deleted_at": "2024-01-01",
                    "tag_id": 1,
                    "user_id": 2,
                }
            ]
        },
    }
    obj = ReportHouseholdResource(**data)
    assert isinstance(obj.movement, list)
    assert isinstance(obj.feeding, list)
    assert isinstance(obj.drinking, list)


def test_report_weight_frame():
    frame = ReportWeightFrame(index=1, weight=2.0, change=0.5, food_type_id=1, target_weight=3.0)
    assert frame.index == 1
    assert frame.weight == 2.0
    assert frame.change == 0.5
    assert frame.food_type_id == 1
    assert frame.target_weight == 3.0
