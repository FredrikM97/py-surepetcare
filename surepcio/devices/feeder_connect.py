import logging
from datetime import datetime
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.const import API_ENDPOINT_V1
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import BowlPosition
from surepcio.enums import BowlType
from surepcio.enums import CloseDelay
from surepcio.enums import FeederTrainingMode
from surepcio.enums import FoodType
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class BowlState(ImprovedErrorMixin):
    position: BowlPosition = BowlPosition.UNKNOWN
    food_type: FoodType = FoodType.UNKNOWN
    substance_type: Optional[int] = None
    current_weight: Optional[float] = None
    last_filled_at: Optional[datetime] = None
    last_zeroed_at: Optional[datetime] = None
    last_fill_weight: Optional[float] = None
    fill_percent: Optional[int] = None


class BowlSetting(ImprovedErrorMixin):
    food_type: FoodType
    target: int


class Bowls(ImprovedErrorMixin):
    settings: list[BowlSetting]
    type: Optional[BowlType] = None


class Lid(ImprovedErrorMixin):
    close_delay: CloseDelay


class Control(BaseControl):
    lid: Optional[Lid] = None
    bowls: Optional[Bowls] = None
    tare: Optional[int] = None
    training_mode: Optional[FeederTrainingMode] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    bowl_status: Optional[list[BowlState]] = None


class FeederConnect(DeviceBase):
    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.FEEDER_CONNECT

    @property
    def photo(self) -> str:
        return "https://www.surepetcare.io/assets/assets/products/feeder.7ff330c9e368df01d256156b6fc797bb.png"

    def refresh(self):
        def parse(response):
            if not response:
                return self
            self.status = Status(**{**self.status.model_dump(), **response["data"]})
            self.control = Control(**{**self.control.model_dump(), **response["data"]})
            return self

        command = Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )
        return command

    @property
    def rssi(self) -> Optional[int]:
        """Return the RSSI value."""
        return self.status.signal.device_rssi if self.status.signal else None

    def set_bowls(self, bowls: Bowls) -> Command:
        """Set bowls settings"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from set_bowls on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(bowls=bowls).model_dump(),
            callback=parse,
        )

    def set_lid(self, lid: Lid) -> Command:
        """Set lid settings"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from set_lid on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(lid=lid).model_dump(),
            callback=parse,
        )

    def set_tare(self, tare: int) -> Command:
        """Set tare settings"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from set_tare on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(tare=tare).model_dump(),
            callback=parse,
        )

    def set_training_mode(self, training_mode: int) -> Command:
        """Set training_mode settings"""

        def parse(response):
            if not response:
                return self
            # Unclear what to do with the data.. Should we refresh or is there any callback info?
            logger.info("Parse callback from set_training_mode on device")
            return self

        return Command(
            "PUT",
            f"{API_ENDPOINT_V1}/device/{self.id}/control",
            params=Control(training_mode=training_mode).model_dump(),
            callback=parse,
        )
