from dataclasses import dataclass
from typing import Any

from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import BowlPosition
from surepetcare.enums import FoodType
from surepetcare.enums import ProductId


@dataclass
class BowlState:
    position: BowlPosition
    food_type: FoodType
    substance_type: int
    current_weight: float
    last_filled_at: str
    last_zeroed_at: str
    last_fill_weight: str
    fill_percent: int


@dataclass
class BowlTargetWeight:
    food_type: FoodType
    full_weight: int  # Target weight for the bowl


class BowlMixin:
    _data: dict[str, Any]

    @property
    def lid_delay(self) -> float:
        return int(self._data["control"]["lid"]["close_delay"])

    @property
    def bowls(self):
        raw_status = self._data["status"].get("bowl_status", [])
        return [
            BowlState(
                position=BowlPosition(entry.get("index", 0)),
                food_type=FoodType(entry.get("food_type", -1)),
                substance_type=entry.get("substance_type", 0),
                current_weight=entry.get("current_weight", 0.0),
                last_filled_at=entry.get("last_filled_at", ""),
                last_zeroed_at=entry.get("last_zeroed_at", ""),
                last_fill_weight=entry.get("last_fill_weight", 0.0),
                fill_percent=entry.get("fill_percent", 0),
            )
            for entry in raw_status
        ]

    @property
    def bowl_targets(self):
        # Map each dict in bowls['settings'] to BowlTargetWeight
        settings = self._data["control"]["bowls"]["settings"]
        return [
            BowlTargetWeight(
                food_type=FoodType(entry.get("food_type", 0)), full_weight=entry.get("target", 0)
            )
            for entry in settings
        ]

    @property
    def tare(self):
        return self._data["control"]["tare"]


class FeederConnect(SurepyDevice, BowlMixin):
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
            self._data = response["data"]
            return self

        command = Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )
        return command

    @property
    def rssi(self) -> int:
        """Return the RSSI value."""
        return self._data["status"]["signal"]["device_rssi"]
