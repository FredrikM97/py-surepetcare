import logging
from dataclasses import dataclass
from typing import Any

from surepetcare.const import API_ENDPOINT_V1
from surepetcare.const import API_ENDPOINT_V2
from surepetcare.helper import validate_date_fields

logger = logging.getLogger(__name__)


class PetHouseholdReport:
    def __init__(self, client, household_id: int, pet_id: int) -> None:
        self._data: dict[str, Any] = {}
        self.client = client

        self.household_id = household_id
        self.pet_id = pet_id

    @validate_date_fields("from_date", "to_date")
    async def fetch(self, from_date: str, to_date: str, event_type: int | None = None) -> None:
        """Fetch pet history data from the API."""

        params: dict[str, Any] = {"From": from_date, "To": to_date}

        if event_type is not None and event_type not in [1, 2, 3]:
            raise ValueError("event_type can only contain 1, 2, or 3")
        if event_type is not None:
            params["EventType"] = event_type

        logger.info(
            f"Fetching pet history data pet_id={self.pet_id},household_id={self.household_id}, \
            **params={params}"
        )
        self._data = (
            await self.client.get(
                f"{API_ENDPOINT_V2}/report/household/{self.household_id}/pet/{self.pet_id}/aggregate",
                params=params,
            )
        )["data"]

    @property
    def feeding(self):
        return self._data["feeding"]

    @property
    def movement(self):
        return self._data["movement"]

    @property
    def drinking(self):
        return self._data["drinking"]

    @property
    def consumption_habit(self):
        return self._data["consumption_habit"]

    @property
    def consumption_alert(self):
        return self._data["consumption_alert"]


@dataclass
class PetFeeding:
    id: int
    tag: int
    device_id: int
    change: int
    time: str


class Pet:
    def __init__(self, client, data: dict) -> None:
        self._data = data
        self.client = client

        self._id = data["id"]
        self._household_id = data["household_id"]
        self._name = data["name"]
        self._tag = data["tag"]["id"]

    @validate_date_fields("from_date")
    async def get_pet_dashboard(self, from_date: str, pet_ids: list[int]) -> str:
        """Old API endpoint for fetching pet dashboard data"""
        return await self.client.get(
            f"{API_ENDPOINT_V1}/dashboard/pet", params={"From": from_date, "PetId": pet_ids}
        )

    def history(self) -> PetHouseholdReport:
        return PetHouseholdReport(self.client, self._household_id, self._id)

    @property
    def id(self) -> int:
        return self._id

    @property
    def household_id(self) -> int:
        return self._household_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag(self) -> str:
        return self._tag

    def feeding(self) -> PetFeeding:
        return PetFeeding(
            id=self._data["status"]["feeding"]["id"],
            tag=self._data["status"]["feeding"]["tag_id"],
            device_id=self._data["status"]["feeding"]["device_id"],
            change=self._data["status"]["feeding"]["change"],
            time=self._data["status"]["feeding"]["at"],
        )
