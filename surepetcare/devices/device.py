import logging
from abc import ABC
from abc import abstractmethod
from typing import Optional

from pydantic import Field

from surepetcare.command import Command
from surepetcare.devices.entities import BaseControl
from surepetcare.devices.entities import BaseStatus
from surepetcare.devices.entities import DeviceInfo
from surepetcare.devices.entities import PetInfo
from surepetcare.entities.battery_mixin import BatteryMixin
from surepetcare.enums import ProductId

logger = logging.getLogger(__name__)


class SurepyBase(ABC):
    status: BaseStatus = Field(default=BaseStatus)
    control: BaseControl = Field(default=BaseControl)

    @property
    @abstractmethod
    def product(self) -> ProductId:
        raise NotImplementedError("Subclasses must implement product_id")

    @property
    def product_id(self) -> int:
        return self.product.value

    @property
    def product_name(self) -> str:
        return self.product.name

    def __str__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

    def refresh(self) -> Command:
        """Refresh the device data."""
        raise NotImplementedError("Subclasses must implement refresh method")


class SurepyDevice(SurepyBase, BatteryMixin):
    device_info = Field(default=DeviceInfo)

    @property
    def parent_device_id(self) -> Optional[int]:
        return self.device_info.parent_device_id

    @property
    def available(self) -> Optional[bool]:
        return self.status.online if self.status is not None else None

    @property
    def photo(self) -> str:
        """Return the url path for device photo."""
        return ""

    @property
    def id(self) -> Optional[int]:
        return self.device_info.id

    @property
    def household_id(self) -> int:
        return self.device_info.household_id

    @property
    def name(self) -> str:
        return self.device_info.name


class SurepyPet(SurepyBase):
    device_info = Field(default=PetInfo)

    @property
    def available(self) -> Optional[bool]:
        return self.status.online

    @property
    def photo(self) -> str:
        """Return the url path for device photo."""
        return ""

    @property
    def id(self) -> Optional[int]:
        return self.device_info.id

    @property
    def household_id(self) -> int:
        return self.device_info.household_id

    @property
    def name(self) -> str:
        return self.device_info.name
