from typing import Any
from typing import Optional

from pydantic import ConfigDict
from pydantic import model_validator

from surepetcare.entities.error_mixin import ImprovedErrorMixin


class FlattenWrappersMixin(ImprovedErrorMixin):
    extras: Optional[dict] = None
    model_config = ConfigDict(extra="allow")


class PetTag(FlattenWrappersMixin):
    id: int
    tag: str
    supported_product_ids: Optional[list[int]] = None
    version: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PetPhoto(FlattenWrappersMixin):
    id: int
    title: str
    location: str
    hash: str
    uploading_user_id: int
    version: int
    created_at: str
    updated_at: str


class BaseInfo(FlattenWrappersMixin):
    @model_validator(mode="before")
    def ignore_status_control(cls, values):
        # Remove 'status' and 'control' from input if present
        values.pop("status", None)
        values.pop("control", None)
        return values


class DeviceInfo(BaseInfo):
    id: int
    name: str
    household_id: int
    parent_device_id: Optional[int] = None
    product_id: int


class PetInfo(BaseInfo):
    id: int
    name: str
    household_id: int
    tag_id: int
    photo: PetPhoto
    tag: PetTag


class BaseControl(FlattenWrappersMixin):
    @model_validator(mode="before")
    def extract_status(cls, values):
        # If 'status' is present, use it; else use values directly
        if "control" in values and isinstance(values["control"], dict):
            return values["control"]
        return values


class Signal(FlattenWrappersMixin):
    device_rssi: Optional[int] = None


class BaseStatus(FlattenWrappersMixin):
    battery: Optional[float] = None
    learn_mode: Optional[bool] = None
    signal: Optional[Signal] = None
    version: Optional[Any] = None
    online: Optional[bool] = None

    @model_validator(mode="before")
    def extract_status(cls, values):
        # If 'status' is present, use it; else use values directly
        if "status" in values and isinstance(values["status"], dict):
            return values["status"]
        return values
