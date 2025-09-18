import logging
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.const import API_ENDPOINT_V1
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Control(BaseControl):
    led_mode: Optional[int] = None
    pairing_mode: Optional[int] = None


class Status(BaseStatus):
    led_mode: Optional[int] = None
    pairing_mode: Optional[int] = None


class Hub(DeviceBase[Control, Status]):
    """Representation of a Hub device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.HUB

    @property
    def photo(self) -> str:
        return (
            "https://www.surepetcare.io/assets/assets/products/hub/hub.6475b3a385180ab8fb96731c4bfd1eda.png"
        )

    def refresh(self):
        """Refresh the device status and control settings from the API."""

        def parse(response) -> "Hub":
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

    def set_led_mode(self, led_mode: int) -> Command:
        """Set let_mode settings"""

        def parse(response) -> "Hub":
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from set_led_mode on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(led_mode=led_mode).model_dump(),
            callback=parse,
        )

    def set_pairing_mode(self, pairing_mode: int) -> Command:
        """Set pairing_mode settings"""

        def parse(response) -> "Hub":
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from set_pairing_mode on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(pairing_mode=pairing_mode).model_dump(),
            callback=parse,
        )
