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

    def set_curfew(self, curfew: Curfew) -> Command:
        """Set the flap curfew times, using the household's timezone"""
        return self.set_control(curfew=curfew)

    def set_curfew_enabled(self, enabled: bool) -> Command:
        """Toggle the existing schedule without losing its times."""
        if self.control.curfew is None:
            raise ValueError("Cannot enable or disable a curfew without a schedule")
        return self.set_curfew(
            self.control.curfew.model_copy(update={"enabled": enabled})
        )
