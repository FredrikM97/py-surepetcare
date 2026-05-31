import logging
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DoorDeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import Curfew
from surepcio.devices.entities import Locking
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import FlapLocking
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Control(BaseControl):
    curfew: Optional[Curfew] = None
    locking: Optional[FlapLocking] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    locking: Optional[Locking] = None


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
