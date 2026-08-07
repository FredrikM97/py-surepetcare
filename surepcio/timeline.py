import json
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

    @property
    def is_look_through(self) -> bool:
        """Return True when the pet looked through without crossing the flap."""
        return self.direction == DoorDirection.LOOKED_THROUGH

    @property
    def is_entry(self) -> bool:
        """Return True when the pet entered the house."""
        return self.direction == DoorDirection.ENTERED

    @property
    def is_exit(self) -> bool:
        """Return True when the pet left the house."""
        return self.direction == DoorDirection.LEFT


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
    weights: list = []

    @property
    def data_parsed(self) -> dict | None:
        """Return the JSON-parsed ``data`` field, or None if absent or null."""
        if not self.data or self.data == "null":
            return None
        try:
            return json.loads(self.data)
        except (ValueError, TypeError):
            return None

    @property
    def primary_movement(self) -> MovementResource | None:
        """Return the first movement entry, or None if there are none."""
        return self.movements[0] if self.movements else None

    @property
    def is_movement_event(self) -> bool:
        """Return True when this is a Movement event (type 0)."""
        return self.event_type == TimelineEventType.MOVEMENT
