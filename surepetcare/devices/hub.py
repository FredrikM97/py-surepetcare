from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId


class Hub(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.HUB

    def refresh(self):
        def parse(response):
            if response['status'] == 304:
                return self
            self._raw_data = response['data']
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )
