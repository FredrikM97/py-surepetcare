from datetime import datetime

from pydantic import Field

from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import DoorDirection, DoorSide, TimelineEventType


class MovementResource(ImprovedErrorMixin):
    """Represents a single movement entry within a timeline event."""

    id: int | None = None
    device_id: int | None = None
    tag_id: int | None = None
    user_id: int | None = None
    direction: DoorDirection | None = None
    side: DoorSide | None = None
    movement_type: int | None = Field(default=None, alias="type")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WeightFrame(ImprovedErrorMixin):
    """Represents a single weight reading within a weight resource."""

    id: int | None = None
    index: int | None = None
    current_weight: int | None = None
    change: int | None = None
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
    product_id: int | None = None
    tag_id: int | None = None


class TimelineEvent(ImprovedErrorMixin):
    """Represents a single event returned by the timeline API."""

    id: int
    event_type: TimelineEventType | None = Field(default=None, alias="type")
    data: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    households: list[TimelineEntityInfo] = Field(default_factory=list)
    devices: list[TimelineEntityInfo] = Field(default_factory=list)
    movements: list[MovementResource] = Field(default_factory=list)
    pets: list[TimelineEntityInfo] = Field(default_factory=list)
    tags: list[TimelineEntityInfo] = Field(default_factory=list)
    users: list[TimelineEntityInfo] = Field(default_factory=list)
    weights: list[WeightResource] = Field(default_factory=list)

    @property
    def is_movement_event(self) -> bool:
        """Return True when this is a Movement event (type 0)."""
        return self.event_type == TimelineEventType.MOVEMENT

    @property
    def is_feeding_event(self) -> bool:
        """Return True when this is a Feeding event (type 22)."""
        return self.event_type == TimelineEventType.FEEDING
