import logging
from typing import Optional

from .dual_scan_connect import DualScanConnect
from .dual_scan_pet_door import DualScanPetDoor
from .feeder_connect import FeederConnect
from .hub import Hub
from .no_id_dog_bowl_connect import NoIdDogBowlConnect
from .pet import Pet
from .pet_door import PetDoor
from .poseidon_connect import PoseidonConnect
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)

DEVICE_CLASS_REGISTRY = {
    ProductId.PET: Pet,
    ProductId.HUB: Hub,
    ProductId.PET_DOOR: PetDoor,
    ProductId.FEEDER_CONNECT: FeederConnect,
    ProductId.DUAL_SCAN_CONNECT: DualScanConnect,
    ProductId.DUAL_SCAN_PET_DOOR: DualScanPetDoor,
    ProductId.POSEIDON_CONNECT: PoseidonConnect,
    ProductId.NO_ID_DOG_BOWL_CONNECT: NoIdDogBowlConnect,
}


def load_device_class(product: ProductId | int) -> Optional[type]:
    cls = DEVICE_CLASS_REGISTRY.get(ProductId.find(product))
    if cls is None:
        logger.warning("Unknown product id: %r (type: %s)", product, type(product).__name__)
    return cls
