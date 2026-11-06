import logging

from surepcio.enums import ProductId

from .device import SurePetCareBase
from .dual_scan_connect import DualScanConnect
from .dual_scan_pet_door import DualScanPetDoor
from .feeder_connect import FeederConnect
from .hub import Hub
from .no_id_dog_bowl_connect import NoIdDogBowlConnect
from .pet import Pet
from .pet_door import PetDoor
from .poseidon_connect import PoseidonConnect

logger = logging.getLogger(__name__)

DEVICE_CLASS_REGISTRY: dict[ProductId, type[SurePetCareBase]] = {
    ProductId.PET: Pet,
    ProductId.HUB: Hub,
    ProductId.PET_DOOR: PetDoor,
    ProductId.FEEDER_CONNECT: FeederConnect,
    ProductId.DUAL_SCAN_CONNECT: DualScanConnect,
    ProductId.DUAL_SCAN_PET_DOOR: DualScanPetDoor,
    ProductId.POSEIDON_CONNECT: PoseidonConnect,
    ProductId.NO_ID_DOG_BOWL_CONNECT: NoIdDogBowlConnect,
}


def load_device_class(product: ProductId | int) -> type[SurePetCareBase] | None:
    """Load the device class based on the product ID."""
    cls = DEVICE_CLASS_REGISTRY.get(ProductId.find(product))
    if cls is None:
        logger.warning(
            "Unknown product id: %r (type: %s)", product, type(product).__name__
        )
    return cls


def get_device_features(product_id: ProductId | int | str | None) -> frozenset[str]:
    """Describe supported configuration features, including persisted product IDs."""
    if product_id is None:
        return frozenset()
    try:
        product = ProductId(int(product_id))
    except (TypeError, ValueError):
        return frozenset()
    device_class = load_device_class(product)
    return device_class.features if device_class is not None else frozenset()
