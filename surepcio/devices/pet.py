import logging
from datetime import datetime
from datetime import timezone
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic import field_validator

from .device import PetBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import BowlPosition
from surepcio.enums import FoodType
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class ReportHouseholdMovementResource(ImprovedErrorMixin):
    """Represents a movement resource in the household report."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    device_id: Optional[int] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None
    from_: Optional[datetime] = Field(default=None, alias="from")
    to: Optional[datetime] = None
    duration: Optional[int] = None
    entry_device_id: Optional[int] = None
    entry_user_id: Optional[int] = None
    exit_device_id: Optional[int] = None
    exit_user_id: Optional[int] = None
    active: Optional[bool] = None
    exit_movement_id: Optional[int] = None
    entry_movement_id: Optional[int] = None


class ReportWeightFrame(ImprovedErrorMixin):
    """Represents a weight frame in the household report."""

    index: Optional[BowlPosition] = None
    weight: Optional[float] = None
    change: Optional[float] = None
    food_type_id: Optional[FoodType] = None
    target_weight: Optional[float] = None


class ReportHouseholdFeedingResource(ImprovedErrorMixin):
    """Represents a feeding resource in the household report."""

    from_: datetime = Field(alias="from")
    to: datetime
    duration: int
    context: int
    bowl_count: int
    device_id: int
    weights: list[ReportWeightFrame] = Field(default_factory=list)


class ReportHouseholdDrinkingResource(ImprovedErrorMixin):
    """Represents a drinking resource in the household report."""

    from_: Optional[datetime] = Field(default=None, alias="from")
    to: Optional[datetime] = None
    duration: Optional[int] = None
    context: Optional[str] = None
    bowl_count: Optional[int] = None
    device_id: Optional[int] = None
    weights: Optional[list[float]] = None
    actual_weight: Optional[float] = None
    entry_user_id: Optional[int] = None
    exit_user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None


class ReportHouseholdResource(ImprovedErrorMixin):
    movement: list[ReportHouseholdMovementResource] = Field(default_factory=list)
    feeding: list[ReportHouseholdFeedingResource] = Field(default_factory=list)
    drinking: list[ReportHouseholdDrinkingResource] = Field(default_factory=list)

    @field_validator("movement", "feeding", "drinking", mode="before")
    def extract_datapoints(v):
        if isinstance(v, dict) and "datapoints" in v:
            return v["datapoints"]
        return v


class Control(ImprovedErrorMixin):
    pass


class Status(ImprovedErrorMixin):
    report: ReportHouseholdResource = Field(default_factory=ReportHouseholdResource)


class Pet(PetBase[Control, Status]):
    controlCls = Control
    statusCls = Status

    def __init__(self, data: dict, **kwargs) -> None:
        super().__init__(data, **kwargs)
        # DateTime from user datetime to UTC timezone
        self.last_fetched_datetime: datetime = datetime.now(ZoneInfo(self.timezone)).astimezone(timezone.utc)

    @property
    def available(self) -> bool:
        """Static until figured out how to handle pet availability."""
        return True

    @property
    def photo(self) -> str | None:
        if self.entity_info.photo is None:
            return None
        return self.entity_info.photo.location

    def refresh(self) -> Command:
        """Refresh the pet's report data."""
        return self.fetch_report()

    def fetch_report(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        event_type: int | None = None,
    ) -> Command:
        def parse(response):
            self.status = Status(
                **{**self.status.model_dump(), "report": ReportHouseholdResource(**response["data"])}
            )
            self.control = Control(**{**self.control.model_dump(), **response["data"]})
            self.last_fetched_datetime = datetime.now(ZoneInfo(self.timezone))
            return self

        params = {}

        if not from_date:
            from_date = self.last_fetched_datetime
        params["From"] = from_date.isoformat()

        if not to_date:
            to_date = datetime.now(ZoneInfo(self.timezone)).astimezone(timezone.utc)
        params["To"] = to_date.isoformat()

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
    def tag(self) -> int | None:
        if self.entity_info.tag is None:
            logger.warning("Pet tag is not set")
            return None
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
