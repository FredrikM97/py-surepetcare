import logging
from datetime import time
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.const import API_ENDPOINT_V1
from surepcio.devices.entities import DevicePetTag
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Curfew(ImprovedErrorMixin):
    enabled: bool
    lock_time: time
    unlock_time: time


class Locking(ImprovedErrorMixin):
    mode: int = 0


class Control(BaseControl):
    curfew: Optional[list[Curfew]] = None
    locking: Optional[int] = None
    fail_safe: Optional[int] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    locking: Optional[Locking] = None


class DualScanConnect(DeviceBase):
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
            self.tags = [DevicePetTag(**tag) for tag in response["data"].get("tags", [])]
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )

    def set_curfew(self, curfew: list[Curfew]) -> Command:
        """Set the flap curfew times, using the household's timezone"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from curfew on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(curfew=curfew).model_dump(),
            callback=parse,
        )

    def set_locking(self, locking: int) -> Command:
        """Set locking mode"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from locking on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(locking=locking).model_dump(),
            callback=parse,
        )

    def set_failsafe(self, failsafe: int) -> Command:
        """Set failsafe mode"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from failsafe on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(fail_safe=failsafe).model_dump(),
            callback=parse,
        )
