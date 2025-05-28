import pytest
from surepetcare.entities.pet import Pet, PetHouseholdReport

class DummyClient:
    def __init__(self):
        self.last_args = None
    async def get(self, endpoint, params=None):
        self.last_args = (endpoint, params)
        # Simulate API response for PetHouseholdReport
        return {"data": {
            "feeding": "feed-data",
            "movement": "move-data",
            "drinking": "drink-data",
            "consumption_habit": "habit-data",
            "consumption_alert": "alert-data"
        }}

@pytest.mark.asyncio
async def test_pethouseholdreport_fetch_and_properties():
    client = DummyClient()
    report = PetHouseholdReport(client, household_id=1, pet_id=2)
    # event_type not in [1,2,3] should raise
    with pytest.raises(ValueError):
        await report.fetch("2024-01-01", "2024-01-02", event_type=99)
    # valid event_type
    await report.fetch("2024-01-01", "2024-01-02", event_type=1)
    assert report.feeding == "feed-data"
    assert report.movement == "move-data"
    assert report.drinking == "drink-data"
    assert report.consumption_habit == "habit-data"
    assert report.consumption_alert == "alert-data"

@pytest.mark.asyncio
async def test_pet_get_pet_dashboard():
    class DummyClient:
        async def get(self, endpoint, params=None):
            return "dashboard-data"
    pet = Pet(DummyClient(), {"id": 1, "household_id": 2, "name": "N", "tag": {"id": 3}})
    result = await pet.get_pet_dashboard("2024-01-01", [1])
    assert result == "dashboard-data"


def test_pet_history_returns_report():
    pet = Pet(object(), {"id": 1, "household_id": 2, "name": "N", "tag": {"id": 3}})
    report = pet.history()
    assert isinstance(report, PetHouseholdReport)
    assert report.household_id == 2
    assert report.pet_id == 1
