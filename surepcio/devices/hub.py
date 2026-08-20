import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import HubLedMode, HubPairMode, ProductId

from .device import BaseControl, BaseStatus, DeviceBase

logger = logging.getLogger(__name__)


class Control(BaseControl):
    led_mode: HubLedMode | None = None
    pairing_mode: HubPairMode | None = None


class Status(BaseStatus):
    led_mode: HubLedMode | None = None
    pairing_mode: HubPairMode | None = None


class Hub(DeviceBase[Control, Status]):
    """Representation of a Hub device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.HUB

    @property
    def photo(self) -> str:
        return "https://www.surepetcare.io/assets/assets/products/hub/hub.6475b3a385180ab8fb96731c4bfd1eda.png"

    def refresh(self):
        """Refresh the device status and control settings from the API."""

        def parse(response: SurePetcareResponse) -> "Hub":
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

    def set_led_mode(self, led_mode: HubLedMode) -> Command:
        """Set let_mode settings"""
        return self.set_control(led_mode=led_mode)

    def set_pairing_mode(self, pairing_mode: HubPairMode) -> Command:
        """Set pairing_mode settings"""
        return self.set_control(pairing_mode=pairing_mode)
