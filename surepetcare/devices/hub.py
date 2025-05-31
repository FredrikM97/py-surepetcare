from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_V2
from surepetcare.enums import ProductId


class Hub(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.HUB

    def refresh(self):
        def parse(response):
            self._raw_data = response
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V2}/product/{self.product_id}/device/{self.id}/control",
            callback=parse,
        )
