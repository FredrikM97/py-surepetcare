from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId

class DualScanPetDoor(SurepyDevice):
    product_id:ProductId = ProductId.DUAL_SCAN_PET_DOOR
    
