import logging
from datetime import datetime
from datetime import timedelta
from typing import Optional

from pydantic import Field
from pydantic import model_validator

from .device import SurepyPet
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.devices.entities import FlattenWrappersMixin
from surepetcare.enums import ProductId

logger = logging.getLogger(__name__)


class ReportHouseholdMovementResource(FlattenWrappersMixin):
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


class ReportWeightFrame(FlattenWrappersMixin):
    """Represents a weight frame in the household report."""

    index: Optional[int] = None
    weight: Optional[float] = None
    change: Optional[float] = None
    food_type_id: Optional[int] = None
    target_weight: Optional[float] = None


class ReportHouseholdFeedingResource(FlattenWrappersMixin):
    """Represents a feeding resource in the household report."""

    from_: str = Field(alias="from")
    to: str
    duration: int
    context: int
    bowl_count: int
    device_id: int
    weights: list[ReportWeightFrame] = Field(default_factory=list)


class ReportHouseholdDrinkingResource(FlattenWrappersMixin):
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


class ReportHouseholdResource(FlattenWrappersMixin):
    movement: list[ReportHouseholdMovementResource] = Field(default_factory=list)
    feeding: list[ReportHouseholdFeedingResource] = Field(default_factory=list)
    drinking: list[ReportHouseholdDrinkingResource] = Field(default_factory=list)

    @model_validator(mode="before")
    def flatmap_datapoints(cls, values):
        if not values:
            return values
        new_values = {}
        for key in ("movement", "feeding", "drinking"):
            section = values.get(key)
            if isinstance(section, dict) and "datapoints" in section:
                new_values[key] = section["datapoints"]

        return new_values


class Control(FlattenWrappersMixin):
    pass


class Status(FlattenWrappersMixin):
    report: ReportHouseholdResource = Field(default_factory=ReportHouseholdResource)


class Pet(SurepyPet):
    def __init__(self, data: dict) -> None:
        try:
            super().__init__(data)
            self.control: Control = Control(**data)
            self.status: Status = Status(**data)
        except Exception as e:
            logger.warning("Error while storing data %s", data)
            raise e
        self.last_fetched_datetime: str | None = None

    @property
    def available(self) -> bool:
        """Static untill figured out how to handle pet availability."""
        return True

    @property
    def photo(self) -> str:
        if self.entity_info.photo is None:
            raise ValueError("household_id is not set")
        return self.entity_info.photo.location

    def refresh(self) -> Command:
        """Refresh the pet's report data."""
        return self.fetch_report()

    def fetch_report(
        self, from_date: str | None = None, to_date: str | None = None, event_type: int | None = None
    ) -> Command:
        def parse(response):
            if all(not v["datapoints"] for v in response["data"].values()):
                return self
            self.status.report = ReportHouseholdResource(**response["data"])
            self.control = Control(**{**self.control.model_dump(), **response["data"]})
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

    @property
    def product(self) -> ProductId:
        return ProductId.PET

    @property
    def tag(self) -> int:
        if self.entity_info.tag is None:
            raise ValueError("household_id is not set")
        return self.entity_info.tag.id

    @property
    def feeding(self) -> list[ReportHouseholdFeedingResource]:
        return self.status.report.feeding

    @property
    def movement(self) -> list[ReportHouseholdMovementResource]:
        return self.status.report.movement

    @property
    def drinking(self) -> list[ReportHouseholdDrinkingResource]:
        return self.status.report.drinking
