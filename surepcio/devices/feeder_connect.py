import logging
from datetime import datetime
from typing import Optional

from .device import BaseControl
from .device import BaseStatus
from .device import DeviceBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import DevicePetTag
from surepcio.devices.entities import FlattenWrappersMixin
from surepcio.enums import BowlPosition
from surepcio.enums import CloseDelay
from surepcio.enums import FoodType
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class BowlState(FlattenWrappersMixin):
    position: BowlPosition = BowlPosition.LEFT
    food_type: FoodType = FoodType.UNKNOWN
    substance_type: Optional[int] = None
    current_weight: Optional[float] = None
    last_filled_at: datetime
    last_zeroed_at: datetime
    last_fill_weight: Optional[float] = None
    fill_percent: Optional[int] = None


class BowlTargetWeight(FlattenWrappersMixin):
    food_type: FoodType = FoodType.DRY
    full_weight: Optional[int] = None


class Lid(FlattenWrappersMixin):
    close_delay: CloseDelay


class Control(BaseControl):
    lid: Optional[Lid] = None
    bowls: Optional[BowlTargetWeight] = None
    tare: Optional[int] = None
    training_mode: Optional[int] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    bowl_status: Optional[list[BowlState]] = None


class FeederConnect(DeviceBase):
    def __init__(self, data: dict, **kwargs) -> None:
        try:
            super().__init__(data, **kwargs)
            self.status: Status = Status(**data)
            self.control: Control = Control(**data)
        except Exception as e:
            logger.warning("Error while storing data %s", data)
            raise e

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
            self.tags = [DevicePetTag(**tag) for tag in response["data"].get("tags", [])]
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
