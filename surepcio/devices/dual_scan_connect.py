import logging
from datetime import time
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import FlattenWrappersMixin
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Curfew(FlattenWrappersMixin):
    enabled: bool
    lock_time: time
    unlock_time: time


class Control(BaseControl):
    curfew: Optional[list[Curfew]] = None
    locking: Optional[int] = None
    fail_safe: Optional[int] = None
    fast_polling: Optional[bool] = None


class Locking(FlattenWrappersMixin):
    mode: int = 0


class Status(BaseStatus):
    locking: Optional[Locking] = None


class DualScanConnect(DeviceBase):
    def __init__(self, data: dict, **kwargs) -> None:
        try:
            super().__init__(data, **kwargs)
            self.status: Status = Status(**data)
            self.control: Control = Control(**data)
        except Exception as e:
            logger.warning("Error while storing data %s", data)
            raise e

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
