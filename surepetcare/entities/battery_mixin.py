import logging

from surepetcare.const import BATT_VOLTAGE_FULL
from surepetcare.const import BATT_VOLTAGE_LOW


logger: logging.Logger = logging.getLogger(__name__)


class BatteryMixin:
    _data: dict

    @property
    def battery_level(self) -> int | None:
        """Return battery level in percent."""
        return self.calculate_battery_level()

    def calculate_battery_level(
        self,
        voltage_full: float = BATT_VOLTAGE_FULL,
        voltage_low: float = BATT_VOLTAGE_LOW,
        num_batteries: int = 4,
    ) -> int | None:
        """Return battery voltage."""

        try:
            voltage_diff = voltage_full - voltage_low
            battery_voltage = float(self._data["status"]["battery"])
            voltage_per_battery = battery_voltage / num_batteries
            voltage_per_battery_diff = voltage_per_battery - voltage_low

            return max(min(int(voltage_per_battery_diff / voltage_diff * 100), 100), 0)

        except (KeyError, TypeError, ValueError) as error:
            logger.debug("error while calculating battery level: %s", error)
            return None
