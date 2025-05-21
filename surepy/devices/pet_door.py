from surepy.devices.base import BaseDevice
from surepy.enums import ProductId

class PetDoor(BaseDevice):
    product_id:ProductId = ProductId.PET_DOOR