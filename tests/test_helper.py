import asyncio

import pytest

from surepetcare.helper import data_exist_validation
from surepetcare.helper import validate_date_fields


class DummyDataExist:
    def __init__(self):
        self._data = {"foo": 1}
        self._raw_data = {"foo": 1}

    @data_exist_validation
    def do_something(self):
        return True


def test_data_exist_validation():
    d = DummyDataExist()
    assert d.do_something() is True
    d._raw_data = None
    with pytest.raises(Exception):
        d.do_something()


def test_validate_date_fields_valid():
    class DummyDate:
        @validate_date_fields("date")
        async def foo(self, date):
            return date

    d = DummyDate()
    # valid date
    assert asyncio.run(d.foo("2024-01-01")) == "2024-01-01"
    assert asyncio.run(d.foo("2024-01-01T12:00:00+0000")) == "2024-01-01T12:00:00+0000"


def test_validate_date_fields_invalid():
    class DummyDate:
        @validate_date_fields("date")
        async def foo(self, date):
            return date

    d = DummyDate()
    with pytest.raises(ValueError):
        asyncio.run(d.foo("not-a-date"))
