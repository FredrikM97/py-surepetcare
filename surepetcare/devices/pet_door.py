from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId


class PetDoor(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.PET_DOOR

    def refresh(self):
        def parse(response):
            if not response:
                return self
            self._data = response["data"]
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )
