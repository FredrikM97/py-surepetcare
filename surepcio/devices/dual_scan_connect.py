import logging

from surepcio.command import Command
from surepcio.devices.entities import Curfew, Locking
from surepcio.entities.door import DoorDeviceBase
from surepcio.enums import FlapLocking, ProductId

from .device import (
    BaseControl,
    BaseStatus,
)

logger = logging.getLogger(__name__)


class Control(BaseControl):
    curfew: list[Curfew] | None = None
    locking: FlapLocking | None = None
    fail_safe: int | None = None
    fast_polling: bool | None = None


class Status(BaseStatus):
    locking: Locking | None = None


class DualScanConnect(DoorDeviceBase[Control, Status]):
    """Representation of a Dual Scan Connect device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_CONNECT

    def set_curfew(self, curfew: list[Curfew]) -> Command:
        """Set the flap curfew times, using the household's timezone"""
        return self.set_control(curfew=curfew)
