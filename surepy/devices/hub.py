from surepy.const import API_ENDPOINT_V2
from surepy.devices.base import BaseDevice
from surepy.enums import ProductId

class Hub(BaseDevice):
    product_id:ProductId = ProductId.HUB
    
    async def fetch(self) -> None:
        self._raw_data =  await self.client.get(self.api_endpoint)
