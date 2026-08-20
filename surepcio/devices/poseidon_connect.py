import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import BowlState, SurePetcareResponse
from surepcio.enums import ProductId

from .device import BaseControl, BaseStatus, DeviceBase

logger = logging.getLogger(__name__)


class Control(BaseControl):
    learn_mode: bool | None = None
    fast_polling: bool | None = None


class Status(BaseStatus):
    bowl_status: list[BowlState] | None = None


class PoseidonConnect(DeviceBase[Control, Status]):
    """Representation of a Poseidon Connect device."""

    controlCls = Control
    statusCls = Status

    def refresh(self):
        """Refresh the device status and control settings from the API."""

        def parse(response: SurePetcareResponse) -> "PoseidonConnect":
            if not response.data:
                return self

            self.status = self.statusCls(
                **{**self.status.model_dump(), **response.data["data"]}
            )
            self.control = self.controlCls(
                **{**self.control.model_dump(), **response.data["data"]}
            )
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            parse=parse,
        )

    @property
    def product(self) -> ProductId:
        return ProductId.POSEIDON_CONNECT
