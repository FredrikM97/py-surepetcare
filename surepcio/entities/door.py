"""Shared door status and commands."""

from datetime import UTC, datetime

from surepcio.command import Command
from surepcio.devices.device import DeviceBase
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import FlapLocking


class DoorDeviceBase[C: ImprovedErrorMixin, S: ImprovedErrorMixin](DeviceBase[C, S]):
    """Base class for door devices."""

    features = frozenset({"location_labels", "pet_profiles"})

    @property
    def is_curfew_active(self) -> bool:
        curfew_value = getattr(self.control, "curfew", None)
        curfews = (
            curfew_value
            if isinstance(curfew_value, list)
            else ([curfew_value] if curfew_value else [])
        )
        # The API reports curfew lock/unlock times in UTC, so compare
        # against the current UTC time rather than the host's local time.
        now = datetime.now(UTC).time()
        return any(
            c.enabled is True
            and c.lock_time is not None
            and c.unlock_time is not None
            and (
                (c.lock_time <= c.unlock_time and c.lock_time <= now <= c.unlock_time)
                or (
                    c.lock_time > c.unlock_time
                    and (now >= c.lock_time or now <= c.unlock_time)
                )
            )
            for c in curfews
        )

    def set_locking(self, locking: FlapLocking) -> Command:
        """Set locking mode"""
        return self.set_control(locking=locking)

    def set_failsafe(self, failsafe: int) -> Command:
        """Set failsafe mode"""
        return self.set_control(fail_safe=failsafe)
