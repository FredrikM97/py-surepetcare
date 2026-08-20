import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import Curfew, Locking, SurePetcareResponse
from surepcio.enums import FlapLocking, ProductId

from .device import BaseControl, BaseStatus, DoorDeviceBase

logger = logging.getLogger(__name__)


class Control(BaseControl):
    curfew: Curfew | None = None
    locking: FlapLocking | None = None
    fast_polling: bool | None = None


class Status(BaseStatus):
    locking: Locking | None = None


class PetDoor(DoorDeviceBase[Control, Status]):
    """Representation of a Pet Door device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.PET_DOOR

    def refresh(self):
        """Refresh the device status and control settings from the API."""

        def parse(response: SurePetcareResponse) -> "PetDoor":
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

    def set_curfew(self, curfew: Curfew) -> Command:
        """Set the flap curfew times, using the household's timezone"""
        return self.set_control(curfew=curfew)
