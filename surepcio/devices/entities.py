from datetime import datetime
from datetime import time
from typing import Any
from typing import Optional

from pydantic import field_serializer
from pydantic import model_validator

from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import FlapLocking


class PetTag(ImprovedErrorMixin):
    """Represents a Pet Tag."""

    id: int
    tag: str
    supported_product_ids: Optional[list[int]] = None
    version: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DevicePetTag(ImprovedErrorMixin):
    """Represents a Pet Tag assigned to a Device."""

    id: Optional[int] = None
    device_id: Optional[int] = None
    index: Optional[int] = None
    profile: Optional[int] = None
    version: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PetPhoto(ImprovedErrorMixin):
    """Represents a Pet Photo."""

    id: int
    title: Optional[str] = None
    location: str
    hash: str
    uploading_user_id: int
    version: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EntityInfo(ImprovedErrorMixin):
    """Represents basic information about an entity."""

    id: int
    name: str
    household_id: int
    product_id: int
    tag_id: Optional[int] = None
    photo: Optional[PetPhoto] = None
    tag: Optional[PetTag] = None
    parent_device_id: Optional[int] = None

    @model_validator(mode="before")
    def ignore_status_control(cls, values):
        # Remove 'status' and 'control' from input if present
        values.pop("status", None)
        values.pop("control", None)
        return values


class BaseControl(ImprovedErrorMixin):
    """Base class for device control settings."""

    tags: Optional[list[DevicePetTag]] = None

    @model_validator(mode="before")
    def extract_control(cls, values):
        merged = {}
        if "control" not in values and "tags" not in values:
            return values
        if "control" in values:
            merged.update(values["control"])
        if "tags" in values and values["tags"]:
            merged["tags"] = values["tags"]
        # Return None if merged is empty (length 0), else merged
        return merged if len(merged) > 0 else {}


class Signal(ImprovedErrorMixin):
    """Represents signal information."""

    device_rssi: Optional[int] = None


class BaseStatus(ImprovedErrorMixin):
    """Base class for device status information."""

    battery: Optional[float] = None
    learn_mode: Optional[bool] = None
    signal: Optional[Signal] = None
    version: Optional[Any] = None
    online: Optional[bool] = None

    @model_validator(mode="before")
    def extract_status(cls, values):
        if "status" in values and isinstance(values["status"], dict):
            return values["status"]
        return values


class Curfew(ImprovedErrorMixin):
    enabled: bool
    lock_time: time
    unlock_time: time

    @field_serializer("lock_time", "unlock_time")
    def serialize_time(self, value: time, _info):
        return value.strftime("%H:%M")


class Locking(ImprovedErrorMixin):
    mode: Optional[FlapLocking] = None
