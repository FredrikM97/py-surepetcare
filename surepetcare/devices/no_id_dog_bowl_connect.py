from surepetcare.devices.base import SurepyDevice
from surepetcare.enums import ProductId


class NoIdDogBowlConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.NO_ID_DOG_BOWL_CONNECT
