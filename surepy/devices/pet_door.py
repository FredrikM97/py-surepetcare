from surepy.devices.base import SurepyDevice
from surepy.enums import ProductId

class PetDoor(SurepyDevice):
    product_id:ProductId = ProductId.PET_DOOR