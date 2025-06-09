import asyncio

import pytest

from surepetcare.helper import data_exist_validation
from surepetcare.helper import validate_date_fields


@pytest.fixture
def dummy_data_exist():
    class DummyDataExist:
        def __init__(self):
            self._data = {"foo": 1}
            self._raw_data = {"foo": 1}

        @data_exist_validation
        def do_something(self):
            return True

    return DummyDataExist()


def test_data_exist_validation(dummy_data_exist):
    """Test data_exist_validation decorator raises if _raw_data is None."""
    d = dummy_data_exist
    assert d.do_something() is True
    d._raw_data = None
    with pytest.raises(Exception):
        d.do_something()


@pytest.fixture
def dummy_date():
    class DummyDate:
        @validate_date_fields("date")
        async def foo(self, date):
            return date

    return DummyDate()


@pytest.mark.parametrize(
    "date_str",
    [
        "2024-01-01",
        "2024-01-01T12:00:00+0000",
    ],
)
def test_validate_date_fields_valid(dummy_date, date_str):
    """Test validate_date_fields accepts valid date strings."""
    d = dummy_date
    assert asyncio.run(d.foo(date_str)) == date_str


@pytest.mark.parametrize(
    "date_str",
    [
        "not-a-date",
        "2024-13-01",
        "2024-01-32",
    ],
)
def test_validate_date_fields_invalid(dummy_date, date_str):
    """Test validate_date_fields raises ValueError for invalid date strings."""
    d = dummy_date
    with pytest.raises(ValueError):
        asyncio.run(d.foo(date_str))
