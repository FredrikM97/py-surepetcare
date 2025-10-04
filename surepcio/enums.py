from enum import Enum
from enum import IntEnum


class SureEnum(IntEnum):
    """Sure base enum."""

    def __str__(self) -> str:
        return self.name.title()


class ProductId(SureEnum):
    """Sure Entity Types."""

    PET = 0  # Dummy just to simplify the pet
    HUB = 1
    PET_DOOR = 3
    FEEDER_CONNECT = 4
    DUAL_SCAN_CONNECT = 6
    DUAL_SCAN_PET_DOOR = 10
    POSEIDON_CONNECT = 8
    NO_ID_DOG_BOWL_CONNECT = 32

    @classmethod
    def find(cls, value: int):
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError:
            return None


class BowlPosition(SureEnum):
    """Feeder Bowl position."""

    UNKNOWN = -1
    ONE = 0
    TWO = 1
    BOTH = 2  # Does not really exist but made for large bowls


class CloseDelay(SureEnum):
    """Feeder Close Delay."""

    FASTER = 0
    NORMAL = 4
    SLOWER = 20


class Location(SureEnum):
    """Locations."""

    INSIDE = 1
    OUTSIDE = 2
    UNKNOWN = -1


class FoodType(SureEnum):
    """Food Types."""

    NOT_SET = 0
    WET = 1
    DRY = 2
    BOTH = 3
    UNKNOWN = -1


class BowlType(SureEnum):
    """Number of Bowls in Feeder"""

    LARGE = 1
    TWO_SMALL = 4


class BowlTypeOptions(Enum):
    """Bowl type and food type combinations for Feeder."""

    LARGE_WET = (BowlType.LARGE, [FoodType.WET])
    LARGE_DRY = (BowlType.LARGE, [FoodType.DRY])
    TWO_SMALL_WET_WET = (BowlType.TWO_SMALL, [FoodType.WET, FoodType.WET])
    TWO_SMALL_WET_DRY = (BowlType.TWO_SMALL, [FoodType.WET, FoodType.DRY])
    TWO_SMALL_DRY_WET = (BowlType.TWO_SMALL, [FoodType.DRY, FoodType.WET])
    TWO_SMALL_DRY_DRY = (BowlType.TWO_SMALL, [FoodType.DRY, FoodType.DRY])

    @property
    def bowl_type(self):
        return self.value[0]

    @property
    def food_types(self):
        return self.value[1]


class FeederTrainingMode(SureEnum):
    """Feeder Training Modes."""

    DISABLED = 0
    STEP_1 = 1
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4


class FlapLocking(SureEnum):
    """Flap Locking Modes."""

    UNLOCKED = 0
    ALLOW_IN = 1
    ALLOW_OUT = 2
    LOCKED = 3


class PetLocation(SureEnum):
    """Pet Location."""

    UNKNOWN = 0
    INSIDE = 1
    OUTSIDE = 2


class PetDeviceLocationProfile(SureEnum):
    """Pet Location."""

    NO_RESTRICTION = 2
    INDOOR_ONLY = 3


class ModifyDeviceTag(Enum):
    """Modify Device Tag Action."""

    ADD = "PUT"
    REMOVE = "DELETE"


class HubLedMode(SureEnum):
    NONE = 0
    WEAK = 4
    STRONG = 1


class HubPairMode(SureEnum):
    OFF = 0
    ON = 1


class SubstanceType(SureEnum):
    """Substance Types."""

    WATER = 1
    FOOD = 2
