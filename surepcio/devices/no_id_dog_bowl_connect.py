import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import ProductId

from .device import BaseControl, BaseStatus, DeviceBase

logger = logging.getLogger(__name__)


class Control(BaseControl):
    pass


class Status(BaseStatus):
    pass


class NoIdDogBowlConnect(DeviceBase[Control, Status]):
    """Representation of a No ID Dog Bowl Connect device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.NO_ID_DOG_BOWL_CONNECT

    def refresh(self) -> Command:
        """Refresh the device status and control settings from the API."""

        def parse(response: SurePetcareResponse) -> "NoIdDogBowlConnect":
            if not response.data:
                return self
            self.status = Status(
                **{**self.status.model_dump(), **response.data["data"]}
            )
            self.control = Control(
                **{**self.control.model_dump(), **response.data["data"]}
            )
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            parse=parse,
        )
