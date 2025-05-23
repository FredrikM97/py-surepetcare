from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId


class NoIdDogBowlConnect(SurepyDevice):
    @property
    def product(self) -> ProductId:
        return ProductId.NO_ID_DOG_BOWL_CONNECT
