import logging
from datetime import datetime
from typing import Optional

from pydantic import Field

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import BowlPosition
from surepcio.enums import BowlType
from surepcio.enums import CloseDelay
from surepcio.enums import FeederTrainingMode
from surepcio.enums import FoodType
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class BowlState(ImprovedErrorMixin):
    position: BowlPosition = Field(default=BowlPosition.UNKNOWN, alias="index")
    food_type: FoodType = FoodType.UNKNOWN
    substance_type: Optional[int] = None
    current_weight: Optional[float] = None
    last_filled_at: Optional[datetime] = None
    last_zeroed_at: Optional[datetime] = None
    last_fill_weight: Optional[float] = None
    fill_percent: Optional[int] = None


class BowlSetting(ImprovedErrorMixin):
    food_type: Optional[FoodType]
    target: Optional[int]


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
    # pet_status: Optional[dict] = None
    bowl_status: Optional[list[BowlState]] = None


class FeederConnect(DeviceBase[Control, Status]):
    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.FEEDER_CONNECT

    @property
    def photo(self) -> str:
        return "https://www.surepetcare.io/assets/assets/products/feeder.7ff330c9e368df01d256156b6fc797bb.png"

    def refresh(self):
        """Refresh the device status and control settings from the API."""
        return self._refresh_device_status()

    def _refresh_device_status(self):
        def parse(response) -> "FeederConnect":
            if not response:
                return self
            self.status = self.statusCls(**{**self.status.model_dump(), **response["data"]})
            self.control = self.controlCls(**{**self.control.model_dump(), **response["data"]})

            # Post-process bowl_status based on bowls.type
            bowls_type = None
            if self.control and self.control.bowls and self.control.bowls.type:
                bowls_type = self.control.bowls.type

            if bowls_type is not None and self.status.bowl_status:
                if bowls_type == BowlType.LARGE_BOWL:
                    # Use only the first bowl (assume it's the left bowl), set its position to MIDDLE
                    if self.status.bowl_status:
                        bowl = self.status.bowl_status[0]
                        bowl.position = BowlPosition.MIDDLE
                        self.status.bowl_status = [bowl]
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
        return self.set_control(bowls=bowls)

    def set_lid(self, lid: Lid) -> Command:
        """Set lid settings"""
        return self.set_control(lid=lid)

    def set_tare(self, tare: int) -> Command:
        """Set tare settings"""
        return self.set_control(tare=tare)

    def set_training_mode(self, training_mode: int) -> Command:
        """Set training_mode settings"""
        return self.set_control(training_mode=training_mode)
