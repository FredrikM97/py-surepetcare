from datetime import datetime
import logging
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import Field

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.const import API_ENDPOINT_V1
from surepcio.devices.entities import BaseControl
from surepcio.devices.entities import BaseStatus
from surepcio.devices.entities import EntityInfo
from surepcio.entities.battery_mixin import BatteryMixin
from surepcio.enums import FlapLocking, ModifyDeviceTag
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)

C = TypeVar("C", bound=BaseControl)
S = TypeVar("S", bound=BaseStatus)


class ModelFactoryMixin(Generic[C, S]):
    controlCls: type[C] = BaseControl
    statusCls: type[S] = BaseStatus


class SurePetCareBase(ABC, ModelFactoryMixin[C, S]):
    """Base class for Sure PetCare entities."""

    entity_info: EntityInfo = Field(default_factory=EntityInfo)

    def __init__(self, data: dict, timezone=None, **kwargs) -> None:
        try:
            self.entity_info = EntityInfo(**{**data, "product_id": self.product_id})
            self.status: S = self.statusCls(**data)
            self.control: C = self.controlCls(**data)
        except Exception as e:
            logger.warning("Error while storing data %s", data)
            raise e
        self.timezone = timezone

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
        return f"<{self.__class__.__name__} id={self.entity_info.id} name={self.entity_info.name}>"

    def refresh(self) -> Command | list[Command]:
        """Refresh the device data."""
        raise NotImplementedError("Subclasses must implement refresh method")


class DeviceBase(SurePetCareBase[C, S], BatteryMixin):
    """Representation of a Sure PetCare Device."""

    @property
    def parent_device_id(self) -> Optional[int]:
        return self.entity_info.parent_device_id

    @property
    def available(self) -> Optional[bool]:
        return self.status.online if self.status is not None else None

    @property
    def photo(self) -> str | None:
        """Return the url path for device photo."""
        return None

    @property
    def id(self) -> Optional[int]:
        return self.entity_info.id

    @property
    def household_id(self) -> int:
        if self.entity_info.household_id is None:
            raise ValueError("household_id is not set")
        return self.entity_info.household_id

    @property
    def name(self) -> Optional[str]:
        return self.entity_info.name

    def set_tag(self, tag_id: int, action: ModifyDeviceTag) -> Command:
        """Add tag/microchip to device."""
        return Command(
            method=action.value,
            endpoint=f"{API_ENDPOINT_V1}/device/{self.id}/tag/{tag_id}/async",
            device=self,
            chain=lambda _: self.refresh(),
        )

    def set_control(self, **control_settings: Any) -> Command:
        """Universal setter for control settings. Inherit the self.control type and can take any input."""
        return Command(
            method="PUT",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}/control/async",
            params=self.controlCls(**control_settings).model_dump(),
            device=self,
            chain=lambda _: self.refresh(),
        )


class DoorDeviceBase(DeviceBase[C, S]):
    """Base class for door devices."""

    @property
    def is_curfew_active(self) -> bool:
        curfews = (
            self.control.curfew
            if isinstance(self.control.curfew, list)
            else ([self.control.curfew] if self.control.curfew else [])
        )
        now = datetime.now().time()
        return any(
            c.enabled
            and (
                (c.lock_time <= c.unlock_time and c.lock_time <= now <= c.unlock_time)
                or (c.lock_time > c.unlock_time and (now >= c.lock_time or now <= c.unlock_time))
            )
            for c in curfews
        )

    def set_locking(self, locking: FlapLocking) -> Command:
        """Set locking mode"""
        return self.set_control(locking=locking)

    def set_failsafe(self, failsafe: int) -> Command:
        """Set failsafe mode"""
        return self.set_control(fail_safe=failsafe)


class PetBase(SurePetCareBase[C, S]):
    """Representation of a Sure PetCare Pet."""

    @property
    def available(self) -> Optional[bool]:
        return self.status.online

    @property
    def photo(self) -> str | None:
        """Return the url path for device photo."""
        return None

    @property
    def id(self) -> Optional[int]:
        return self.entity_info.id

    @property
    def household_id(self) -> int:
        return self.entity_info.household_id

    @property
    def name(self) -> Optional[str]:
        return self.entity_info.name
