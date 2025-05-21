from dataclasses import dataclass
from datetime import datetime
from surepy.enums import BowlPosition, FoodType
from surepy.devices.base import BaseDevice
from surepy.const import API_ENDPOINT_V1, API_ENDPOINT_V2
from surepy.enums import ProductId


class FeederConnect(BaseDevice):
    product_id:ProductId = ProductId.FEEDER_CONNECT

    async def fetch(self) -> None:
        self._data =  (await self.client.get(f"{API_ENDPOINT_V1}/device/{self.device_id}"))['data']

    @property
    def lid_close_delay(self) -> float:
        return float(self._data["control"]['lid_delay']['close_delay'])
    
    @property
    def weight(self) -> float:
        return float(self._data["weight"])

    @property
    def change(self) -> float:
        return float(self._data["change"])

    @property
    def target(self) -> int | None:
        return int(self._data["target"]) if "target" in self._data else None

    @property
    def index(self) -> int | None:
        return int(self._data["index"]) if "index" in self._data else None

    @property
    def food_type_id(self) -> int | None:
        return int(self._data["food_type_id"]) if "food_type_id" in self._data else None

    @property
    def food_type(self) -> str | None:
        return FoodType(self.food_type_id).name.capitalize() if self.food_type_id else None

    @property
    def position(self) -> str | None:
        return BowlPosition(self.index).name.capitalize() if self.index else None

    