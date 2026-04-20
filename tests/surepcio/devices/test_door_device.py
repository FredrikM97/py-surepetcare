from datetime import datetime
from datetime import time

import pytest

from surepcio.devices.device import DoorDeviceBase
from surepcio.devices.entities import BaseControl
from surepcio.devices.entities import BaseStatus
from surepcio.devices.entities import Curfew
from surepcio.enums import ProductId


class FakeDoor(DoorDeviceBase[BaseControl, BaseStatus]):
    @property
    def product(self) -> ProductId:
        return ProductId.PET_DOOR

    def refresh(self):
        raise NotImplementedError("refresh is not used in this test")


class DummyDateTime:
    def __init__(self, fixed_datetime: datetime):
        self._fixed_datetime = fixed_datetime

    def now(self):
        return self._fixed_datetime


@pytest.mark.parametrize(
    "curfew_values, now, expected",
    [
        # Single curfew inside the same-day interval
        (
            [Curfew(enabled=True, lock_time=time(6, 0), unlock_time=time(18, 0))],
            datetime(2025, 1, 1, 10, 0),
            True,
        ),
        # Single curfew outside the same-day interval
        (
            [Curfew(enabled=True, lock_time=time(6, 0), unlock_time=time(18, 0))],
            datetime(2025, 1, 1, 19, 0),
            False,
        ),
        # Single curfew crossing midnight active before midnight
        (
            [Curfew(enabled=True, lock_time=time(22, 0), unlock_time=time(6, 0))],
            datetime(2025, 1, 1, 23, 0),
            True,
        ),
        # Single curfew crossing midnight active after midnight
        (
            [Curfew(enabled=True, lock_time=time(22, 0), unlock_time=time(6, 0))],
            datetime(2025, 1, 2, 1, 0),
            True,
        ),
        # Single curfew crossing midnight inactive during the day
        (
            [Curfew(enabled=True, lock_time=time(22, 0), unlock_time=time(6, 0))],
            datetime(2025, 1, 1, 13, 0),
            False,
        ),
        # Curfew disabled
        (
            [Curfew(enabled=False, lock_time=time(6, 0), unlock_time=time(18, 0))],
            datetime(2025, 1, 1, 10, 0),
            False,
        ),
        # Single curfew object instead of list
        (
            Curfew(enabled=True, lock_time=time(6, 0), unlock_time=time(18, 0)),
            datetime(2025, 1, 1, 10, 0),
            True,
        ),
    ],
)
def test_is_curfew_active_with_various_times(monkeypatch, curfew_values, now, expected):
    fake = FakeDoor({"id": 1, "household_id": 1})
    fake.control = type("Control", (), {"curfew": curfew_values})()
    monkeypatch.setattr("surepcio.devices.device.datetime", DummyDateTime(now))

    assert fake.is_curfew_active is expected
