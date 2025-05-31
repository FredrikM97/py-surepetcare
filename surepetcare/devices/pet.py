from datetime import datetime
from datetime import timedelta

from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_V2
from surepetcare.entities.pet import ReportHouseholdDrinkingResource
from surepetcare.entities.pet import ReportHouseholdFeedingResource
from surepetcare.entities.pet import ReportHouseholdMovementResource
from surepetcare.entities.pet import ReportHouseholdResource
from surepetcare.enums import ProductId


class Pet(SurepyDevice):
    def __init__(self, data: dict) -> None:
        self._data = data
        self._id = data["id"]
        self._household_id = data["household_id"]
        self._name = data["name"]
        self._tag = data["tag"]["id"]
        self.last_fetched_datetime: str | None = None
        self._report: ReportHouseholdResource | None = None

    def refresh(self) -> Command:
        """Refresh the pet's report data."""
        return self.fetch_report()

    def fetch_report(
        self, from_date: str | None = None, to_date: str | None = None, event_type: int | None = None
    ) -> Command:
        def parse(response):
            self._report = ReportHouseholdResource.model_validate(response["data"])
            self.last_fetched_datetime = datetime.utcnow().isoformat()
            return self

        params = {}

        if not from_date:
            if self.last_fetched_datetime:
                from_date = self.last_fetched_datetime
            else:
                from_date = (datetime.now() - timedelta(hours=24)).isoformat()
        params["From"] = from_date

        # Handle to_date
        if not to_date:
            to_date = datetime.utcnow().isoformat()
        params["To"] = to_date

        if event_type is not None:
            if event_type not in [1, 2, 3]:
                raise ValueError("event_type can only contain 1, 2, or 3")
            params["EventType"] = str(event_type)
        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V2}/report/household/{self.household_id}/pet/{self.id}/aggregate",
            params=params,
            callback=parse,
        )

    def get_pet_dashboard(self, from_date: str, pet_ids: list[int]):
        def parse(response):
            return response

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V2}/dashboard/pet",
            params={"From": from_date, "PetId": pet_ids},
            callback=parse,
        )

    @property
    def product(self) -> ProductId:
        return ProductId.PET

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
    def tag(self) -> int:
        return self._tag

    @property
    def feeding(self) -> list[ReportHouseholdFeedingResource]:
        if self._report is None or self._report.feeding is None:
            return []
        return self._report.feeding

    @property
    def movement(self) -> list[ReportHouseholdMovementResource]:
        if self._report is None or self._report.movement is None:
            return []
        return self._report.movement

    @property
    def drinking(self) -> list[ReportHouseholdDrinkingResource]:
        if self._report is None or self._report.drinking is None:
            return []
        return self._report.drinking
