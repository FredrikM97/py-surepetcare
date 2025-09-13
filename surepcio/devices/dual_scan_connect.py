import logging
from datetime import time
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import FlapLocking, ProductId

logger = logging.getLogger(__name__)


class Curfew(ImprovedErrorMixin):
    enabled: bool
    lock_time: time
    unlock_time: time


class Locking(ImprovedErrorMixin):
    mode: FlapLocking = 0


class Control(BaseControl):
    curfew: Optional[list[Curfew]] = None
    locking: Optional[FlapLocking] = None
    fail_safe: Optional[int] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    locking: Optional[Locking] = None


class DualScanConnect(DeviceBase[Control, Status]):
    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_CONNECT

    def refresh(self):
        def parse(response):
            if not response:
                return self
            self.status = Status(**{**self.status.model_dump(), **response["data"]})
            self.control = Control(**{**self.control.model_dump(), **response["data"]})
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
