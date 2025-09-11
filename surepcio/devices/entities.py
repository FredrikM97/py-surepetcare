from datetime import datetime
from typing import Any
from typing import Optional

from pydantic import ConfigDict
from pydantic import model_validator

from surepcio.entities.error_mixin import ImprovedErrorMixin


class FlattenWrappersMixin(ImprovedErrorMixin):
    model_config = ConfigDict(extra="ignore")


class PetTag(FlattenWrappersMixin):
    id: int
    tag: str
    supported_product_ids: Optional[list[int]] = None
    version: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DevicePetTag(FlattenWrappersMixin):
    id: Optional[int]
    device_id: Optional[int]
    index: Optional[int]
    profile: Optional[int]
    version: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class PetPhoto(FlattenWrappersMixin):
    id: int
    title: Optional[str] = None
    location: str
    hash: str
    uploading_user_id: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class EntityInfo(FlattenWrappersMixin):
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


class BaseControl(FlattenWrappersMixin):
    @model_validator(mode="before")
    def extract_control(cls, values):
        if "control" in values and isinstance(values["control"], dict):
            return values["control"]
        return values


class Signal(FlattenWrappersMixin):
    device_rssi: Optional[int]


class BaseStatus(FlattenWrappersMixin):
    battery: Optional[float]
    learn_mode: Optional[bool]
    signal: Optional[Signal]
    version: Optional[Any]
    online: Optional[bool]

    @model_validator(mode="before")
    def extract_status(cls, values):
        if "status" in values and isinstance(values["status"], dict):
            return values["status"]
        return values
