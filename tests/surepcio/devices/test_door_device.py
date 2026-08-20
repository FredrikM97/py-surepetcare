import time as time_module
from contextlib import ExitStack
from datetime import UTC, datetime, time

import pytest
import time_machine

from surepcio.devices.device import DoorDeviceBase
from surepcio.devices.entities import BaseControl, BaseStatus, Curfew
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
        assert tz is UTC, "is_curfew_active must compare in UTC"
        return self._fixed_datetime.replace(tzinfo=tz)


@pytest.mark.parametrize(
    "curfew_values, now, expected",
    [
        # Single curfew inside the same-day interval
        (
            [Curfew(enabled=True, lock_time=time(6, 0), unlock_time=time(18, 0))],
            datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            True,
        ),
        # Single curfew outside the same-day interval
        (
            [Curfew(enabled=True, lock_time=time(6, 0), unlock_time=time(18, 0))],
            datetime(2025, 1, 1, 19, 0, tzinfo=UTC),
            False,
        ),
        # Single curfew crossing midnight active before midnight
        (
            [Curfew(enabled=True, lock_time=time(22, 0), unlock_time=time(6, 0))],
            datetime(2025, 1, 1, 23, 0, tzinfo=UTC),
            True,
        ),
        # Single curfew crossing midnight active after midnight
        (
            [Curfew(enabled=True, lock_time=time(22, 0), unlock_time=time(6, 0))],
            datetime(2025, 1, 2, 1, 0, tzinfo=UTC),
            True,
        ),
        # Single curfew crossing midnight inactive during the day
        (
            [Curfew(enabled=True, lock_time=time(22, 0), unlock_time=time(6, 0))],
            datetime(2025, 1, 1, 13, 0, tzinfo=UTC),
            False,
        ),
        # Curfew disabled
        (
            [Curfew(enabled=False, lock_time=time(6, 0), unlock_time=time(18, 0))],
            datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            False,
        ),
        # Single curfew object instead of list
        (
            Curfew(enabled=True, lock_time=time(6, 0), unlock_time=time(18, 0)),
            datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            True,
        ),
    ],
)
def test_is_curfew_active_with_various_times(monkeypatch, curfew_values, now, expected):
    fake = FakeDoor({"id": 1, "household_id": 1})
    fake.control = type("Control", (), {"curfew": curfew_values})()
    monkeypatch.setattr("surepcio.devices.device.datetime", DummyDateTime(now))

    assert fake.is_curfew_active is expected


@pytest.mark.skipif(
    not hasattr(time_module, "tzset"),
    reason="requires POSIX tzset to change local time",
)
def test_is_curfew_active_uses_utc_not_host_local_time(monkeypatch) -> None:
    """Curfew times from the API are UTC; a host in UTC+1 must not shift the window."""
    fake = FakeDoor({"id": 1, "household_id": 1})
    fake.control = type(
        "Control",
        (),
        {
            "curfew": [
                Curfew(enabled=True, lock_time=time(21, 0), unlock_time=time(5, 0))
            ]
        },
    )()

    with ExitStack() as cleanup:
        # Ensure tzset is called after TZ restoration, even when assertions fail.
        cleanup.callback(time_module.tzset)
        tz_context = cleanup.enter_context(monkeypatch.context())
        tz_context.setenv("TZ", "Europe/London")  # UTC+1 (BST) on the frozen date
        time_module.tzset()

        # 20:30 UTC is 21:30 local: local clock is past lock_time but UTC is not
        with time_machine.travel("2026-07-06 20:30:00 +00:00", tick=False):
            assert fake.is_curfew_active is False
        with time_machine.travel("2026-07-06 21:30:00 +00:00", tick=False):
            assert fake.is_curfew_active is True
