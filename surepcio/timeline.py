import json
from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    PlainSerializer,
    SerializationInfo,
    ValidationInfo,
    field_serializer,
    field_validator,
)

from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import (
    DoorDirection,
    DoorSide,
    DoorStatus,
    FlapLocking,
    FoodType,
    ProductId,
    TimelineEventType,
)


def enum_name(value: Enum) -> str:
    return value.name


type NamedEnum[T: Enum] = Annotated[
    T, PlainSerializer(enum_name, return_type=str, when_used="json")
]


class MovementResource(ImprovedErrorMixin):
    """Represents a single movement entry within a timeline event."""

    id: int | None = None
    device_id: int | None = None
    tag_id: int | None = None
    user_id: int | None = None
    direction: NamedEnum[DoorDirection] | None = None
    side: NamedEnum[DoorSide] | None = None
    movement_type: NamedEnum[DoorStatus] | None = Field(default=None, alias="type")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WeightFrame(ImprovedErrorMixin):
    """Represents a single weight reading within a weight resource."""

    id: int | None = None
    index: int | None = None
    current_weight: int | float | None = None
    change: int | float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WeightResource(ImprovedErrorMixin):
    """Represents a feeding/drinking weight entry within a timeline event."""

    id: int | None = None
    device_id: int | None = None
    tag_id: int | None = None
    context: int | None = None
    duration: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    frames: list[WeightFrame] = Field(default_factory=list)


class TimelineEntityInfo(ImprovedErrorMixin):
    """Minimal entity reference embedded in a timeline event."""

    id: int
    name: str | None = None
    household_id: int | None = None
    product_id: NamedEnum[ProductId] | None = None
    tag_id: int | None = None


class TimelineData(BaseModel):
    """Base for verified event data shapes, retaining additional API fields."""

    model_config = ConfigDict(extra="allow")


class DoorLockingData(TimelineData):
    """Door-locking configuration included in a timeline event."""

    mode: NamedEnum[FlapLocking] | None = None
    last_mode: NamedEnum[FlapLocking] | None = None
    curfew: list[JsonValue] | None = None


class CurfewLockData(TimelineData):
    """Curfew lock-status observation with API time strings."""

    mode: NamedEnum[FlapLocking] | None = None
    locked: bool | None = None
    time: str | None = None
    lock: str | None = None
    unlock: str | None = None


class BowlDimensions(TimelineData):
    """Dimensions for half and full feeder bowls or plates."""

    half: int | float | None = None
    full: int | float | None = None


class FeederWeightData(TimelineData):
    """Feeder bowl configuration accompanying timeline weight observations."""

    count: int | None = None
    food_type: list[NamedEnum[FoodType] | None] | None = None
    plate: BowlDimensions | None = None
    bowl: BowlDimensions | None = None
    target: list[int | float | None] | None = None
    tare_value: JsonValue = None


class FeederData(TimelineData):
    """Data verified for feeding and feeder weight-change events."""

    encounter_source: JsonValue = None
    weight: FeederWeightData | None = None
    tare_type: JsonValue = None


EVENT_DATA_MODELS: dict[TimelineEventType, type[TimelineData]] = {
    TimelineEventType.DOOR_LOCKING_MODE: DoorLockingData,
    TimelineEventType.CURFEW_LOCK_STATUS: CurfewLockData,
    TimelineEventType.FEEDING: FeederData,
    TimelineEventType.WEIGHT_CHANGED: FeederData,
}


class TimelineEvent(ImprovedErrorMixin):
    """Represents a single event returned by the timeline API."""

    id: int
    event_type: NamedEnum[TimelineEventType] | None = Field(default=None, alias="type")
    data: JsonValue | TimelineData = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    households: list[TimelineEntityInfo] = Field(default_factory=list)
    devices: list[TimelineEntityInfo] = Field(default_factory=list)
    movements: list[MovementResource] = Field(default_factory=list)
    pets: list[TimelineEntityInfo] = Field(default_factory=list)
    tags: list[TimelineEntityInfo] = Field(default_factory=list)
    users: list[TimelineEntityInfo] = Field(default_factory=list)
    weights: list[WeightResource] = Field(default_factory=list)

    @field_validator("data", mode="before")
    @classmethod
    def decode_data(cls, value: object, info: ValidationInfo) -> object:
        """Decode JSON and select typed data only for its corresponding event."""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return value
        event_type = info.data.get("event_type")
        data_model = (
            EVENT_DATA_MODELS.get(event_type) if event_type is not None else None
        )
        if data_model is not None and isinstance(value, dict):
            return data_model.model_validate(value)
        return value

    @field_serializer("data")
    def serialize_data(
        self, value: TimelineData | JsonValue, info: SerializationInfo
    ) -> Any:
        if isinstance(value, TimelineData):
            return value.model_dump(mode=info.mode, exclude_unset=True)
        return value


def build_event_payload(household_id: int, event: TimelineEvent) -> dict[str, Any]:
    """Serialize the complete API event, adding the requesting household ID."""
    return event.model_dump(exclude_none=False, exclude_unset=True) | {
        "household_id": household_id
    }
