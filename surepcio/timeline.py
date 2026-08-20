from datetime import datetime
from typing import Optional

from pydantic import Field

from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import DoorDirection, DoorSide, TimelineEventType


class MovementResource(ImprovedErrorMixin):
    """Represents a single movement entry within a timeline event."""

    id: Optional[int] = None
    device_id: Optional[int] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None
    direction: Optional[DoorDirection] = None
    side: Optional[DoorSide] = None
    movement_type: Optional[int] = Field(default=None, alias="type")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WeightFrame(ImprovedErrorMixin):
    """Represents a single weight reading within a weight resource."""

    id: Optional[int] = None
    index: Optional[int] = None
    current_weight: Optional[int] = None
    change: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WeightResource(ImprovedErrorMixin):
    """Represents a feeding/drinking weight entry within a timeline event."""

    id: Optional[int] = None
    device_id: Optional[int] = None
    tag_id: Optional[int] = None
    context: Optional[int] = None
    duration: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    frames: list[WeightFrame] = []


class TimelineEntityInfo(ImprovedErrorMixin):
    """Minimal entity reference embedded in a timeline event."""

    id: int
    name: Optional[str] = None
    household_id: Optional[int] = None
    product_id: Optional[int] = None
    tag_id: Optional[int] = None


class TimelineEvent(ImprovedErrorMixin):
    """Represents a single event returned by the timeline API."""

    id: int
    event_type: Optional[TimelineEventType] = Field(default=None, alias="type")
    data: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    households: list[TimelineEntityInfo] = []
    devices: list[TimelineEntityInfo] = []
    movements: list[MovementResource] = []
    pets: list[TimelineEntityInfo] = []
    tags: list[TimelineEntityInfo] = []
    users: list[TimelineEntityInfo] = []
    weights: list[WeightResource] = []

    @property
    def is_movement_event(self) -> bool:
        """Return True when this is a Movement event (type 0)."""
        return self.event_type == TimelineEventType.MOVEMENT

    @property
    def is_feeding_event(self) -> bool:
        """Return True when this is a Feeding event (type 22)."""
        return self.event_type == TimelineEventType.FEEDING
