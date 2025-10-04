import logging
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.dual_scan_connect import Curfew
from surepcio.devices.entities import Locking
from surepcio.enums import FlapLocking
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Control(BaseControl):
    curfew: Optional[list[Curfew]] = None
    locking: Optional[FlapLocking] = None
    fail_safe: Optional[int] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    locking: Optional[Locking] = None


class DualScanPetDoor(DeviceBase[Control, Status]):
    """Representation of a Dual Scan Pet Door device."""

    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_PET_DOOR

    def refresh(self):
        """Refresh the device status and control settings from the API."""

        def parse(response) -> "DualScanPetDoor":
            if not response:
                return self
            self.status = BaseStatus(**{**self.status.model_dump(), **response["data"]})
            self.control = BaseControl(**{**self.control.model_dump(), **response["data"]})
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )

    def set_curfew(self, curfew: list[Curfew]) -> Command:
        """Set the flap curfew times, using the household's timezone"""
        return self.set_control(curfew=curfew)

    def set_locking(self, locking: FlapLocking) -> Command:
        """Set locking mode"""
        return self.set_control(locking=locking)

    def set_failsafe(self, failsafe: int) -> Command:
        """Set failsafe mode"""
        return self.set_control(fail_safe=failsafe)
