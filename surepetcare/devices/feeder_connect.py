import logging
from typing import Any
from typing import Optional

from pydantic import ConfigDict
from pydantic import Field

from .device import BaseControl
from .device import BaseStatus
from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.devices.entities import FlattenWrappersMixin
from surepetcare.enums import BowlPosition
from surepetcare.enums import FoodType
from surepetcare.enums import ProductId

logger = logging.getLogger(__name__)


class BowlState(FlattenWrappersMixin):
    position: BowlPosition = Field(default=BowlPosition(0))
    food_type: FoodType = Field(default=FoodType(-1))
    substance_type: int = 0
    current_weight: float = 0.0
    last_filled_at: str = ""
    last_zeroed_at: str = ""
    last_fill_weight: float = 0.0
    fill_percent: int = 0
    model_config = ConfigDict(extra="allow")


class BowlTargetWeight(FlattenWrappersMixin):
    food_type: FoodType = Field(default=FoodType.DRY)
    full_weight: int = 0
    model_config = ConfigDict(extra="allow")


class Control(BaseControl):
    lid: Optional[dict[str, Any]] = None
    bowls: Optional[dict[str, Any]] = None
    tare: Optional[int] = None
    training_mode: Optional[int] = None
    fast_polling: Optional[bool] = None


class Status(BaseStatus):
    bowl_status: Optional[list[dict[str, Any]]] = None


class FeederConnect(SurepyDevice):
    def __init__(self, data: dict) -> None:
        try:
            super().__init__(data)
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
