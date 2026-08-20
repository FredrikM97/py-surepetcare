import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.dual_scan_connect import Curfew
from surepcio.devices.entities import Locking, SurePetcareResponse
from surepcio.enums import FlapLocking, ProductId

from .device import BaseControl, BaseStatus, DoorDeviceBase

logger = logging.getLogger(__name__)


class Control(BaseControl):
    curfew: list[Curfew] | None = None
    locking: FlapLocking | None = None
    fail_safe: int | None = None
    fast_polling: bool | None = None


class Status(BaseStatus):
    locking: Locking | None = None


class DualScanPetDoor(DoorDeviceBase[Control, Status]):
    """Representation of a Dual Scan Pet Door device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_PET_DOOR

    def refresh(self) -> Command:
        """Refresh the device status and control settings from the API."""

        def parse(response: SurePetcareResponse) -> "DualScanPetDoor":
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

    def set_curfew(self, curfew: list[Curfew]) -> Command:
        """Set the flap curfew times, using the household's timezone"""
        return self.set_control(curfew=curfew)
