from datetime import datetime
from datetime import time
from datetime import timezone
from zoneinfo import ZoneInfo

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

    def now(self, tz=None):
        if tz is None:
            return self._fixed_datetime
        return self._fixed_datetime.astimezone(tz)


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
    fake = FakeDoor({"id": 1, "household_id": 1}, tzinfo=timezone.utc)
    fake.control = type("Control", (), {"curfew": curfew_values})()
    monkeypatch.setattr("surepcio.devices.device.datetime", DummyDateTime(now))

    assert fake.is_curfew_active is expected


def test_is_curfew_active_uses_household_timezone(monkeypatch) -> None:
    fake = FakeDoor({"id": 1, "household_id": 1}, tzinfo=ZoneInfo("Europe/London"))
    fake.control = type(
        "Control",
        (),
        {
            "curfew": [
                Curfew(
                    enabled=True,
                    lock_time=time(12, 30),
                    unlock_time=time(13, 30),
                )
            ]
        },
    )()
    monkeypatch.setattr(
        "surepcio.devices.device.datetime",
        DummyDateTime(datetime(2025, 6, 1, 11, 45, tzinfo=timezone.utc)),
    )

    assert fake.is_curfew_active is True


@pytest.mark.parametrize(
    "tz_name, expected",
    [
        ("Europe/Stockholm", True),
        ("America/New_York", False),
    ],
)
def test_is_curfew_active_respects_timezone_conversion(
    monkeypatch, tz_name: str, expected: bool
) -> None:
    fake = FakeDoor({"id": 1, "household_id": 1}, tzinfo=ZoneInfo(tz_name))
    fake.control = type(
        "Control",
        (),
        {
            "curfew": [
                Curfew(
                    enabled=True,
                    lock_time=time(14, 30),
                    unlock_time=time(15, 30),
                )
            ]
        },
    )()
    # 12:45 UTC => 14:45 in Europe/Stockholm and 08:45 in America/New_York.
    monkeypatch.setattr(
        "surepcio.devices.device.datetime",
        DummyDateTime(datetime(2025, 6, 1, 12, 45, tzinfo=timezone.utc)),
    )

    assert fake.is_curfew_active is expected
