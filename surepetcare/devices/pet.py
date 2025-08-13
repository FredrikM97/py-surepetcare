from datetime import datetime
from datetime import timedelta
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator

from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.entities.error_mixin import ImprovedErrorMixin
from surepetcare.enums import ProductId


class ReportHouseholdMovementResource(ImprovedErrorMixin):
    """Represents a movement resource in the household report."""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    device_id: Optional[int] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None
    from_: Optional[str] = Field(default=None, alias="from")
    to: Optional[str] = None
    duration: Optional[int] = None
    entry_device_id: Optional[int] = None
    entry_user_id: Optional[int] = None
    exit_device_id: Optional[int] = None
    exit_user_id: Optional[int] = None
    active: Optional[bool] = None
    exit_movement_id: Optional[int] = None
    entry_movement_id: Optional[int] = None

    @model_validator(mode="before")
    def flatten_data(cls, values):
        # If this resource is wrapped in a 'data' key, flatten it
        if "datapoints" in values and isinstance(values["datapoints"], dict):
            if "data" in values:
                return values["data"]
            return values
        return values

    model_config = ConfigDict(extra="ignore")


class ReportWeightFrame(BaseModel):
    """Represents a weight frame in the household report."""

    index: Optional[int] = None
    weight: Optional[float] = None
    change: Optional[float] = None
    food_type_id: Optional[int] = None
    target_weight: Optional[float] = None


class ReportHouseholdFeedingResource(ImprovedErrorMixin):
    """Represents a feeding resource in the household report."""

    from_: str = Field(alias="from")
    to: str
    duration: int
    context: Optional[str] = None
    bowl_count: Optional[int] = None
    device_id: Optional[int] = None
    weights: Optional[list[ReportWeightFrame]] = None
    actual_weight: Optional[float] = None
    entry_user_id: Optional[int] = None
    exit_user_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None

    @model_validator(mode="before")
    def flatten_data(cls, values):
        if "data" in values and isinstance(values["data"], dict):
            values = values["data"]
        # Convert context to str if it's int
        if "context" in values and not isinstance(values["context"], str):
            values["context"] = str(values["context"])
        # Convert weights to list of dicts if present
        if "weights" in values and isinstance(values["weights"], list):
            weights = []
            for w in values["weights"]:
                if isinstance(w, dict):
                    weights.append(w)
                else:
                    weights.append({"weight": w})
            values["weights"] = weights
        return values


class ReportHouseholdDrinkingResource(ImprovedErrorMixin):
    """Represents a drinking resource in the household report."""

    from_: Optional[str] = Field(default=None, alias="from")
    to: Optional[str] = None
    duration: Optional[int] = None
    context: Optional[str] = None
    bowl_count: Optional[int] = None
    device_id: Optional[int] = None
    weights: Optional[list[float]] = None
    actual_weight: Optional[float] = None
    entry_user_id: Optional[int] = None
    exit_user_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None

    @model_validator(mode="before")
    def flatten_data(cls, values):
        if "datapoints" in values and isinstance(values["datapoints"], dict):
            if "data" in values:
                return values["data"]
            return values
        return values

    model_config = ConfigDict(extra="ignore")


class ReportHouseholdResource(ImprovedErrorMixin):
    pet_id: Optional[int] = None
    device_id: Optional[int] = None
    movement: Optional[list[ReportHouseholdMovementResource]] = None
    feeding: Optional[list[ReportHouseholdFeedingResource]] = None
    drinking: Optional[list[ReportHouseholdDrinkingResource]] = None

    @model_validator(mode="before")
    def flatten_datapoints(cls, values):
        for key in ["movement", "feeding", "drinking"]:
            if key in values and isinstance(values[key], dict) and "datapoints" in values[key]:
                values[key] = values[key]["datapoints"]
        return values

    model_config = ConfigDict(extra="ignore")


class Pet(SurepyDevice):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self._data = data
        self._id = data["id"]
        self._household_id = data["household_id"]
        self._name = data["name"]
        self._tag = data["tag"]["id"]
        self.last_fetched_datetime: str | None = None
        self._report: ReportHouseholdResource | None = None
        self._photo = data.get("photo", {}).get("location", "")

    @property
    def available(self) -> bool:
        """Static untill figured out how to handle pet availability."""
        return True

    @property
    def photo(self) -> str:
        return self._photo

    def refresh(self) -> Command:
        """Refresh the pet's report data."""
        return self.fetch_report()

    def fetch_report(
        self, from_date: str | None = None, to_date: str | None = None, event_type: int | None = None
    ) -> Command:
        def parse(response):
            if not response:
                return self
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
            endpoint=(
                f"{API_ENDPOINT_PRODUCTION}/report/household/{self.household_id}/pet/{self.id}/aggregate"
            ),
            params=params,
            callback=parse,
        )

    def get_pet_dashboard(self, from_date: str, pet_ids: list[int]):
        def parse(response):
            if not response:
                return []
            return response["data"]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/dashboard/pet",
            params={"From": from_date, "PetId": pet_ids},
            callback=parse,
            reuse=False,
        )

    @property
    def product(self) -> ProductId:
        return ProductId.PET

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
