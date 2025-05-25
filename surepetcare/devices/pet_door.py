from surepetcare.devices.base import SurepyDevice
from surepetcare.enums import ProductId


class PetDoor(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.PET_DOOR
