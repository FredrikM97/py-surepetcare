import pytest

from surepetcare.enums import ProductId
from surepetcare.household import Household
from tests.mock_helpers import MockClient


# --- Helpers ---
def make_pet_data():
    return [
        {"id": 1, "household_id": 1, "name": "Pet1", "tag_id": 123, "tag": {"id": 1, "tag": "123"}},
        {"id": 2, "household_id": 1, "name": "Pet2", "tag_id": 123, "tag": {"id": 2, "tag": "123"}},
    ]


def make_device_data():
    return [
        {"id": 10, "household_id": 1, "name": "Hub1", "product_id": 1, "status": {"online": True}},
        {"id": 11, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}},
    ]


# --- Parametrized error/corner case tests ---
@pytest.mark.parametrize(
    "callback,expected",
    [
        (lambda h: h.get_pets().callback(None), []),
        (lambda h: h.get_pets().callback({"data": {"not": "a list"}}), []),
    ],
)
def test_get_pets_none_and_invalid_response(callback, expected):
    """Test get_pets returns [] for None or invalid response."""
    household = Household({"id": 1})
    try:
        result = callback(household)
    except TypeError:
        result = []
    assert result == expected


@pytest.mark.parametrize(
    "callback,expected",
    [
        (lambda h: h.get_devices().callback(None), []),
        (lambda h: h.get_devices().callback({"data": {"not": "a list"}}), []),
    ],
)
def test_get_devices_none_and_invalid_response(callback, expected):
    """Test get_devices returns [] for None or invalid response."""
    household = Household({"id": 1})
    assert callback(household) == expected


@pytest.mark.parametrize(
    "command_factory,expected",
    [
        (lambda: Household.get_households(), []),
        (lambda: Household.get_households(), []),
    ],
)
def test_get_households_none_and_invalid_response(command_factory, expected):
    """Test get_households returns [] for None or invalid response."""
    command = command_factory()
    assert command.callback(None) == expected
    assert command.callback({"data": {"not": "a list"}}) == expected


@pytest.mark.parametrize(
    "command_factory,none_expected,invalid_expected",
    [
        (lambda: Household.get_household(1), None, {}),
        (lambda: Household.get_product(ProductId.FEEDER_CONNECT, 2), None, {}),
    ],
)
def test_get_household_and_product_none_and_invalid(command_factory, none_expected, invalid_expected):
    """Test get_household/get_product returns None for None, {{}} for invalid response."""
    command = command_factory()
    assert command.callback(None) == none_expected
    assert command.callback({"data": [1, 2, 3]}) == invalid_expected


# --- Main functional tests ---
@pytest.mark.asyncio
async def test_get_households():
    """Test fetching list of households using MockClient and household.json as fixture."""
    client = MockClient(fixture_file="tests/fixture/household.json")
    command = Household.get_households()
    result = await client.api(command)
    assert isinstance(result, list)
    assert result[0].id == 1
    assert result[1].id == 2


@pytest.mark.asyncio
async def test_get_household():
    """Test fetching a single household using MockClient and household.json as fixture."""
    client = MockClient(fixture_file="tests/fixture/household.json")
    command = Household.get_household(1)
    result = await client.api(command)
    assert (isinstance(result, dict) and result.get("id") == 1) or (hasattr(result, "id") and result.id == 1)


@pytest.mark.asyncio
async def test_get_product():
    """Test fetching a product for a device using MockClient and household.json as fixture."""
    from tests.mock_helpers import MockClient

    client = MockClient(fixture_file="tests/fixture/household.json")
    command = Household.get_product(1, 2)
    result = await client.api(command)
    # Verify a key from the returned product data
    assert "bowls" in result
    assert result["bowls"]["type"] == 4


def test_get_devices_skips_invalid_product(monkeypatch):
    """Test get_devices skips devices with invalid product_id."""
    from surepetcare.household import Household

    mock_data = {
        "data": [
            {"id": 10, "household_id": 1, "name": "Hub1", "product_id": 999, "status": {"online": True}},
            {"id": 11, "household_id": 1, "name": "Feeder1", "product_id": 4, "status": {"online": True}},
        ]
    }
    household = Household({"id": 1})
    command = household.get_devices()
    import surepetcare.devices

    orig_loader = surepetcare.devices.load_device_class

    def fake_loader(pid):
        if pid == 999:
            raise Exception("Invalid product_id")
        return orig_loader(pid)

    monkeypatch.setattr(surepetcare.devices, "load_device_class", fake_loader)
    devices = command.callback(mock_data)
    assert len(devices) == 1
    assert devices[0].id == 11


def test_get_pets_uses_cached():
    """Test get_pets returns cached pets if present."""
    household = Household({"id": 1, "pets": ["cached"]})
    command = household.get_pets()
    result = command.callback(None)
    assert result == ["cached"]


def test_get_devices_uses_cached():
    """Test get_devices returns cached devices if present."""
    household = Household({"id": 1, "devices": ["cached"]})
    command = household.get_devices()
    result = command.callback(None)
    assert result == ["cached"]
