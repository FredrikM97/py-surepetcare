import pytest
from surepy.entities.devices import Feeder, FeederBowl, Tag, Felaqua, Flap
from surepy.enums import LockState

def make_feeder_data():
    return {'id': 269654,
            'parent_device_id': 123,
            'product_id': 4,
            'household_id': 555,
            'index': 0,
            'name': 'Cat feeder',
            'serial_number': 'XXX',
            'mac_address': '54321',
            'version': 31075,
            'created_at': '2020-03-29T13:42:22+00:00',
            'updated_at': '2025-05-21T08:51:15+00:00',
            'pairing_at': '2023-10-01T13:16:15+00:00',
            'last_new_event_at': '2025-05-21T16:47:13+00:00',
            'control': {'bowls': {'settings': [{'food_type': 2, 'target': 100000},
                {'food_type': 2, 'target': 100000}],
            'type': 4},
            'lid': {'close_delay': 4},
            'tare': 2,
            'training_mode': 0,
            'fast_polling': False},
            'status': {'battery': 5.568,
            'learn_mode': False,
            'signal': {'device_rssi': -79},
            'version': {'device': {'hardware': '9', 'firmware': '406.437'}},
            'online': True}
        }

def test_feeder_bowls_and_tags():
    data = make_feeder_data()
    feeder = Feeder(data)
    assert feeder.bowl_count == 2
    assert len(feeder.bowls) == 2
    assert isinstance(next(iter(feeder.bowls.values())), FeederBowl)
    assert feeder.total_weight == 50.0  # Only one bowl has weight > 0

    # Test bowls' properties
    bowl = feeder.bowls[1]
    assert bowl.name == "Test Feeder Bowl 1"
    assert bowl.weight == 50.0
    assert bowl.change == 5.0
    assert bowl.target == 60
    assert bowl.food_type_id == 1
    assert bowl.food_type is not None
    assert bowl.position is not None

    # Test tags
    assert len(feeder.tags) == 2
    tag = feeder.tags[1]
    assert tag.id == 101
    assert tag.profile() == 1
    assert tag.version() == "v1"
    assert tag.created_at() == "2024-01-01"
    assert tag.updated_at() == "2024-01-02"
    assert isinstance(tag.raw_data(), dict)

def test_feeder_missing_data():
    # Test with missing lunch and tags
    feeder = Feeder({})
    assert feeder.bowl_count == 0
    assert feeder.total_weight == 0.0
    assert len(feeder.tags) == 0

def test_feeder_bowl_missing_fields():
    # Missing optional fields
    data = {"index": 3, "weight": 0, "change": 0}
    feeder = Feeder({})
    bowl = FeederBowl(data, feeder)
    assert bowl.target is None
    assert bowl.food_type_id is None
    assert bowl.food_type is None
    assert bowl.position is not None


class DummyClient:
    async def get(self, endpoint, params=None):
        return {"data": {"feeding": [1, 2, 3]}}

@pytest.mark.asyncio
async def test_pet_fetch_and_feeding():
    client = DummyClient()
    pet = Pet(client, "household_id", "pet_id")
    await pet.fetch("2025-01-01", "2025-02-01")
    assert pet.feeding() == [1, 2, 3]

@pytest.mark.asyncio
async def test_pet_feeding_raises_without_fetch():
    client = DummyClient()
    pet = Pet(client, "household_id", "pet_id")
    with pytest.raises(Exception):
        pet.feeding()