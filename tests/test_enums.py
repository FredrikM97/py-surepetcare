import pytest

from surepetcare.enums import BowlPosition
from surepetcare.enums import FoodType
from surepetcare.enums import Location
from surepetcare.enums import ProductId


@pytest.mark.parametrize(
    "enum_cls, member, value, name, strval",
    [
        (ProductId, ProductId.HUB, 1, "HUB", "Hub"),
        (ProductId, ProductId.PET_DOOR, 3, "PET_DOOR", "Pet_Door"),
        (ProductId, ProductId.FEEDER_CONNECT, 4, "FEEDER_CONNECT", "Feeder_Connect"),
        (ProductId, ProductId.DUAL_SCAN_CONNECT, 6, "DUAL_SCAN_CONNECT", "Dual_Scan_Connect"),
        (ProductId, ProductId.NO_ID_DOG_BOWL_CONNECT, 32, "NO_ID_DOG_BOWL_CONNECT", "No_Id_Dog_Bowl_Connect"),
        (BowlPosition, BowlPosition.LEFT, 0, "LEFT", "Left"),
        (BowlPosition, BowlPosition.RIGHT, 1, "RIGHT", "Right"),
        (Location, Location.INSIDE, 1, "INSIDE", "Inside"),
        (Location, Location.OUTSIDE, 2, "OUTSIDE", "Outside"),
        (Location, Location.UNKNOWN, -1, "UNKNOWN", "Unknown"),
        (FoodType, FoodType.WET, 1, "WET", "Wet"),
        (FoodType, FoodType.DRY, 2, "DRY", "Dry"),
        (FoodType, FoodType.BOTH, 3, "BOTH", "Both"),
        (FoodType, FoodType.UNKNOWN, -1, "UNKNOWN", "Unknown"),
    ],
)
def test_enum_values_and_str(enum_cls, member, value, name, strval):
    """Test enum value, name, and str output."""
    assert member.value == value
    assert member.name == name
    assert str(member) == strval
