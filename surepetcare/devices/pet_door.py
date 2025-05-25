from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId


class PetDoor(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.PET_DOOR
