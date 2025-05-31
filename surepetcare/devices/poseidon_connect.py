from .device import SurepyDevice
from surepetcare.enums import ProductId


class PoseidonConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.POSEIDON_CONNECT
