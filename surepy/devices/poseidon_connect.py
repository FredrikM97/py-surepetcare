from surepy.devices.base import BaseDevice
from surepy.enums import ProductId

class PoseidonConnect(BaseDevice):
    product_id:ProductId = ProductId.POSEIDON_CONNECT
