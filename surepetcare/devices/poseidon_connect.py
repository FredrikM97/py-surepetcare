from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId


class PoseidonConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.POSEIDON_CONNECT
