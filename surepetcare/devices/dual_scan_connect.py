from surepetcare.devices.base import SurepyDevice
from surepetcare.enums import ProductId


class DualScanConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_CONNECT
