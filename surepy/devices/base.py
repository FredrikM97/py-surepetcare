import logging
from abc import ABC
from typing import Optional

from surepy.const import BATT_VOLTAGE_FULL
from surepy.const import BATT_VOLTAGE_LOW
from surepy.enums import ProductId

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


class SurepyDevice(ABC, BatteryMixin):
    product_id: ProductId

    def __init__(self, client, data: dict):
        self._data = data
        self.client = client

        # Initialize device properties
        self._id = data["id"]
        self._household_id = data["household_id"]
        self._name = data["name"]
        self._online = data["status"]["online"]

    @property
    def id(self) -> int:
        return self._id

    @property
    def household_id(self) -> int:
        return self._household_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def online(self) -> bool:
        return self._online

    @property
    def raw_data(self) -> Optional[dict]:
        return self._data

    def __str__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
