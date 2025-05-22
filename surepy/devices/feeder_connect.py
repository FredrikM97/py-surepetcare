from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar
from surepy.enums import BowlPosition, FoodType
from surepy.devices.base import SurepyDevice
from surepy.const import API_ENDPOINT_V1
from surepy.enums import ProductId


@dataclass
class BowlState:
    position: BowlPosition
    food_type: FoodType

class BowlMixin:
    _data:dict[str, Any]
    @property
    def lid_delay(self) -> float:
        return int(self._data["control"]['lid']['close_delay'])

    @property
    def bowls(self) -> list:
        settings = self._data['control']['bowls']['settings']
        return [BowlState(BowlPosition(index), FoodType(bowl['food_type'])) for index, bowl in enumerate(settings)]
    
class FeederConnect(SurepyDevice, BowlMixin):
    product_id:ProductId = ProductId.FEEDER_CONNECT

    async def fetch(self) -> None:
        self._data = (await self.client.get(f"{API_ENDPOINT_V1}/device/{self.id}"))['data']


  

    