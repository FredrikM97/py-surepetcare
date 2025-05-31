from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_V1
from surepetcare.enums import ProductId


class NoIdDogBowlConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.NO_ID_DOG_BOWL_CONNECT

    def refresh(self):
        def parse(response):
            self._raw_data = response
            return self

        return Command(method="GET", endpoint=f"{API_ENDPOINT_V1}/device/{self.id}", callback=parse)
