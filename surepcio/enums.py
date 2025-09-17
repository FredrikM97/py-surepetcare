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
    LEFT = 0
    RIGHT = 1
    MIDDLE = 2  # Does not really exist but made for large bowls


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

    LARGE_BOWL = 1
    TWO_SMALL = 4


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

    INSIDE = 0
    OUTSIDE = 1


class PetDeviceLocationProfile(SureEnum):
    """Pet Location."""

    NO_RESTRICTION = 2
    INDOOR_ONLY = 3
