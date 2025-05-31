from .device import SurepyDevice
from surepetcare.enums import ProductId


class DualScanPetDoor(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_PET_DOOR
