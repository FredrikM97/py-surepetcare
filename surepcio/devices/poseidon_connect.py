import logging
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import BowlState
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Control(BaseControl):
    learn_mode: Optional[bool] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    bowl_status: Optional[list[BowlState]] = None


class PoseidonConnect(DeviceBase[Control, Status]):
    """Representation of a Poseidon Connect device."""

    controlCls = Control
    statusCls = Status

    def refresh(self):
        """Refresh the device status and control settings from the API."""

        def parse(response) -> "PoseidonConnect":
            if not response:
                return self

            self.status = self.statusCls(**{**self.status.model_dump(), **response["data"]})
            self.control = self.controlCls(**{**self.control.model_dump(), **response["data"]})
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )

    @property
    def product(self) -> ProductId:
        return ProductId.POSEIDON_CONNECT
