from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId


class NoIdDogBowlConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.NO_ID_DOG_BOWL_CONNECT

    def refresh(self):
        def parse(response):
            if not response:
                return self
            self._raw_data = response["data"]
            return self

        return Command(method="GET", endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}", callback=parse)
