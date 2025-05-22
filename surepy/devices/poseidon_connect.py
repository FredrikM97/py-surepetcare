from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId

class PoseidonConnect(SurepyDevice):
    product_id:ProductId = ProductId.POSEIDON_CONNECT
