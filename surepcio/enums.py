from enum import Enum
from enum import IntEnum


class SureEnum(IntEnum):
    """Sure base enum."""

    # This breaks stuff so temp remove it..
    # def __str__(self) -> str:
    #    return self.name.title()


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
    NOT_DETERMINED = 5


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
    CURFEW_MODE = 4


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
    STRONG = 1
    # NOT_DETERMINED_1 = 2
    # NOT_DETERMINED_2 = 3
    WEAK = 4
    # NOT_DETERMINED_3 = 128


class HubPairMode(SureEnum):
    DISABLED = 0
    # NOT_DETERMINED_1 = 1
    ON = 2
    # NOT_DETERMINED_2 = 3
    # NOT_DETERMINED_3 = 128


class SubstanceType(SureEnum):
    """Substance Types."""

    WATER = 1
    FOOD = 2


class Tare(SureEnum):
    # Reset bowl weight to zero. Requires lid to be open. LARGE and LEFT share the same value
    DISABLED = 0  # I assume 0 is disabled
    RESET_LARGE = 1
    RESET_LEFT = 1
    RESET_RIGHT = 2
    RESET_BOTH = 3


class RequestStatus(Enum):
    """Request/Control Status for async operations."""

    COMPLETED = 0
    STATUS_1 = 1
    STATUS_2 = 2
    STATUS_3 = 3
    STATUS_4 = 4
    PENDING = 5

    @classmethod
    def not_completed(cls):
        """Return all enum members that are not COMPLETED."""
        return [status.value for status in cls if status != cls.COMPLETED]


class TimelineEventType(SureEnum):
    """Timeline event types from the SurePetCare API."""

    MOVEMENT = 0
    LOW_BATTERY = 1
    NEW_TAG = 2
    NEW_DEVICE = 3
    HUB_PAIRING_MODE = 4
    LEARN_MODE = 5
    DOOR_LOCKING_MODE = 6
    INTRUDER_MOVEMENT = 7
    HUB_CHILD_ONLINE = 9
    PENDING_INVITE = 10
    INVITE_HANDLED = 11
    USER_JOINED_HOUSEHOLD = 12
    NEW_PET = 13
    NEW_PHOTO = 14
    ACCOUNT_CREATED = 17
    DEVICE_ONLINE = 18
    NEW_USER_PROFILE_PHOTO = 19
    CURFEW_LOCK_STATUS = 20
    WEIGHT_CHANGED = 21
    FEEDING = 22
    TARGET_WEIGHT_SET = 23
    TARE = 24
    PET_PERMISSIONS_CHANGED = 25
    WEIGHT_CHANGED_TARGET_MET = 27
    TRAINING_MODE = 28
    POSEIDON_DRINKING = 29
    POSEIDON_WEIGHT_CHANGED = 30
    POSEIDON_TARE = 31
    POSEIDON_WATER_FRESHNESS = 32
    POSEIDON_LOW_WATER = 33
    WATER_REMOVED = 34
    CURFEW_TIMEZONE_CHANGE = 40
    WCI_ALERT = 51
    TARING_REQUIRED = 52
    TARRING_OCCURRED = 53

    @classmethod
    def find(cls, value: int) -> "TimelineEventType | None":
        try:
            return cls(value)
        except ValueError:
            return None


class DoorDirection(SureEnum):
    """Direction of a pet through a door (from SurePetCare timeline movements)."""

    LOOKED_THROUGH = 0
    ENTERED = 1
    LEFT = 2
    UNKNOWN = 3


class DoorSide(SureEnum):
    """Side of the door a pet was on."""

    OUTSIDE = 0
    INSIDE = 1
    UNKNOWN = 2



