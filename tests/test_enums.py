import pytest
from surepetcare.enums import ProductId, SureEnum, BowlPosition, Location, FoodType

def test_productid_enum():
    assert ProductId.HUB == 1
    assert str(ProductId.HUB) == "Hub"
    assert ProductId.PET_DOOR.name == "PET_DOOR"
    assert ProductId.FEEDER_CONNECT.value == 4
    assert ProductId.DUAL_SCAN_CONNECT.name == "DUAL_SCAN_CONNECT"
    assert ProductId.NO_ID_DOG_BOWL_CONNECT.value == 32

def test_bowlposition_enum():
    assert BowlPosition.LEFT == 0
    assert BowlPosition.RIGHT == 1
    assert str(BowlPosition.LEFT) == "Left"

def test_location_enum():
    assert Location.INSIDE == 1
    assert Location.OUTSIDE == 2
    assert Location.UNKNOWN == -1
    assert str(Location.OUTSIDE) == "Outside"

def test_foodtype_enum():
    assert FoodType.WET == 1
    assert FoodType.DRY == 2
    assert FoodType.BOTH == 3
    assert FoodType.UNKNOWN == -1
    assert str(FoodType.BOTH) == "Both"
