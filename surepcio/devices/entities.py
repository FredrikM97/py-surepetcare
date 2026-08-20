from dataclasses import dataclass
from datetime import datetime, time
from typing import Any

from pydantic import Field, field_serializer, model_validator

from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import (
    BowlPosition,
    FlapLocking,
    FoodType,
    PetDeviceLocationProfile,
    SubstanceType,
)


class PetTag(ImprovedErrorMixin):
    """Represents a Pet Tag."""

    id: int
    tag: str
    supported_product_ids: list[int] | None = None
    version: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DevicePetTag(ImprovedErrorMixin):
    """Represents a Pet Tag assigned to a Device."""

    id: int | None = None
    device_id: int | None = None
    index: int | None = None
    profile: PetDeviceLocationProfile | None = None
    version: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PetPhoto(ImprovedErrorMixin):
    """Represents a Pet Photo."""

    id: int
    title: str | None = None
    location: str
    hash: str
    uploading_user_id: int
    version: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EntityInfo(ImprovedErrorMixin):
    """Represents basic information about an entity."""

    id: int
    name: str | None = None
    household_id: int
    product_id: int
    tag_id: int | None = None
    photo: PetPhoto | None = None
    tag: PetTag | None = None
    parent_device_id: int | None = None

    @model_validator(mode="before")
    def ignore_status_control(cls, values):
        # Remove 'status' and 'control' from input if present
        values.pop("status", None)
        values.pop("control", None)
        return values


class BaseControl(ImprovedErrorMixin):
    """Base class for device control settings."""

    tags: list[DevicePetTag] | None = None

    @model_validator(mode="before")
    def extract_control(cls, values):
        merged = {}
        if "control" not in values and "tags" not in values:
            return values
        if "control" in values:
            merged.update(values["control"])
        if values.get("tags"):
            merged["tags"] = values["tags"]
        # Return None if merged is empty (length 0), else merged
        return merged if len(merged) > 0 else {}


class Signal(ImprovedErrorMixin):
    """Represents signal information."""

    device_rssi: int | None = None


class BaseStatus(ImprovedErrorMixin):
    """Base class for device status information."""

    battery: float | None = None
    learn_mode: bool | None = None
    signal: Signal | None = None
    version: Any | None = None
    online: bool | None = None

    @model_validator(mode="before")
    def extract_status(cls, values):
        if "status" in values and isinstance(values["status"], dict):
            return values["status"]
        return values


class Curfew(ImprovedErrorMixin):
    enabled: bool | None = None
    lock_time: time | None = None
    unlock_time: time | None = None

    @field_serializer("lock_time", "unlock_time")
    def serialize_time(self, value: time, _info):
        return value.strftime("%H:%M")


class Locking(ImprovedErrorMixin):
    mode: FlapLocking | None = None


@dataclass
class SurePetcareResponse:
    data: dict | None = None
    status: int = 0
    reason: str | None = None


class BowlState(ImprovedErrorMixin):
    position: BowlPosition | None = Field(default=None, alias="index")
    food_type: FoodType | None = None
    substance_type: SubstanceType | None = None
    current_weight: float | None = None
    last_filled_at: datetime | None = None
    last_zeroed_at: datetime | None = None
    last_fill_weight: float | None = None
    fill_percent: int | None = None
