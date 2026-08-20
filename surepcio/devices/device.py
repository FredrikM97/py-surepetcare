import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, cast

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION, API_ENDPOINT_V1
from surepcio.devices.entities import BaseControl, BaseStatus, EntityInfo
from surepcio.entities.battery_mixin import BatteryMixin
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import FlapLocking, ModifyDeviceTag, ProductId

logger = logging.getLogger(__name__)


class ModelFactoryMixin[C: ImprovedErrorMixin, S: ImprovedErrorMixin]:
    controlCls: type[C] = cast(type[C], BaseControl)
    statusCls: type[S] = cast(type[S], BaseStatus)


class SurePetCareBase[C: ImprovedErrorMixin, S: ImprovedErrorMixin](
    ABC, ModelFactoryMixin[C, S]
):
    """Base class for Sure PetCare entities."""

    entity_info: EntityInfo

    def __init__(self, data: dict, timezone=None, **kwargs) -> None:
        try:
            self.entity_info = EntityInfo(**{**data, "product_id": self.product_id})
            self.status: S = cast(S, self.statusCls(**data))
            self.control: C = cast(C, self.controlCls(**data))
        except Exception:
            logger.warning("Error while storing data %s", data)
            raise
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


class DeviceBase[C: ImprovedErrorMixin, S: ImprovedErrorMixin](
    SurePetCareBase[C, S], BatteryMixin
):
    """Representation of a Sure PetCare Device."""

    @property
    def parent_device_id(self) -> int | None:
        return self.entity_info.parent_device_id

    @property
    def available(self) -> bool | None:
        return getattr(self.status, "online", None) if self.status is not None else None

    @property
    def photo(self) -> str | None:
        """Return the url path for device photo."""
        return None

    @property
    def id(self) -> int | None:
        return self.entity_info.id

    @property
    def household_id(self) -> int:
        if self.entity_info.household_id is None:
            raise ValueError("household_id is not set")
        return self.entity_info.household_id

    @property
    def name(self) -> str | None:
        return self.entity_info.name

    def set_tag(self, tag_id: int, action: ModifyDeviceTag) -> Command:
        """Add tag/microchip to device."""
        return Command(
            method=action.value,
            endpoint=f"{API_ENDPOINT_V1}/device/{self.id}/tag/{tag_id}/async",
            household_id=self.household_id,
            chain=lambda _: self.refresh(),
        )

    def set_control(self, **control_settings: Any) -> Command:
        """Universal setter for control settings. Inherit the self.control type and can take any input."""
        return Command(
            method="PUT",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}/control/async",
            params=self.controlCls(**control_settings).model_dump(),
            household_id=self.household_id,
            chain=lambda _: self.refresh(),
        )


class DoorDeviceBase[C: ImprovedErrorMixin, S: ImprovedErrorMixin](DeviceBase[C, S]):
    """Base class for door devices."""

    @property
    def is_curfew_active(self) -> bool:
        curfew_value = getattr(self.control, "curfew", None)
        curfews = (
            curfew_value
            if isinstance(curfew_value, list)
            else ([curfew_value] if curfew_value else [])
        )
        # The API reports curfew lock/unlock times in UTC, so compare
        # against the current UTC time rather than the host's local time.
        now = datetime.now(UTC).time()
        return any(
            c.enabled
            and (
                (c.lock_time <= c.unlock_time and c.lock_time <= now <= c.unlock_time)
                or (
                    c.lock_time > c.unlock_time
                    and (now >= c.lock_time or now <= c.unlock_time)
                )
            )
            for c in curfews
        )

    def set_locking(self, locking: FlapLocking) -> Command:
        """Set locking mode"""
        return self.set_control(locking=locking)

    def set_failsafe(self, failsafe: int) -> Command:
        """Set failsafe mode"""
        return self.set_control(fail_safe=failsafe)


class PetBase[C: ImprovedErrorMixin, S: ImprovedErrorMixin](SurePetCareBase[C, S]):
    """Representation of a Sure PetCare Pet."""

    @property
    def available(self) -> bool | None:
        return getattr(self.status, "online", None)

    @property
    def photo(self) -> str | None:
        """Return the url path for device photo."""
        return None

    @property
    def id(self) -> int | None:
        return self.entity_info.id

    @property
    def household_id(self) -> int:
        return self.entity_info.household_id

    @property
    def name(self) -> str | None:
        return self.entity_info.name
