import logging
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import BowlState
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import BowlPosition
from surepcio.enums import BowlType
from surepcio.enums import BowlTypeOptions
from surepcio.enums import CloseDelay
from surepcio.enums import FeederTrainingMode
from surepcio.enums import FoodType
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class BowlSetting(ImprovedErrorMixin):
    food_type: Optional[FoodType] = None
    target: Optional[int] = None


class Bowls(ImprovedErrorMixin):
    settings: Optional[list[Optional[BowlSetting]]] = None
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
                if bowls_type == BowlType.LARGE:
                    # Use only the first bowl (assume it's the left bowl), set its position to MIDDLE
                    if self.status.bowl_status:
                        bowl = self.status.bowl_status[0]
                        bowl.position = BowlPosition.BOTH
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

    def set_bowl_type(self, option: BowlTypeOptions) -> object:
        """Set the bowl type/settings on the device using BowlTypeOptions enum."""
        if not isinstance(option, BowlTypeOptions):
            return None
        settings = [{"food_type": ft.value, "target": 0} for ft in option.food_types]
        return self.set_control(
            bowls={
                "type": option.bowl_type.value,
                "settings": settings,
            }
        )

    def get_bowl_type_option(self) -> str | None:
        """Return the BowlTypeOptions name matching the current device bowl settings."""
        bowls = self.control.bowls
        if not bowls or not bowls.type or not bowls.settings:
            return None
        bowl_type = bowls.type
        settings = bowls.settings if isinstance(bowls.settings, list) else list(bowls.settings)
        food_types = tuple(getattr(s, "food_type", None) for s in settings)
        for option in BowlTypeOptions:
            if option.bowl_type == bowl_type and tuple(option.food_types) == tuple(food_types):
                return option.name
        return None
