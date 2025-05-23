from surepy.const import API_ENDPOINT_V2
from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId


class Hub(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.HUB

    async def fetch(self) -> None:
        self._raw_data = await self.client.get(
            f"{API_ENDPOINT_V2}/product/{self.product_id}/device/{self.id}/control"
        )
