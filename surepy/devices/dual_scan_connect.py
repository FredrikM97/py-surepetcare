from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId


class DualScanConnect(SurepyDevice):
    product_id: ProductId = ProductId.DUAL_SCAN_CONNECT
