
from abc import ABC, abstractmethod
import logging
from typing import Optional
from surepy.const import API_ENDPOINT_V2, BATT_VOLTAGE_FULL, BATT_VOLTAGE_LOW
from surepy.enums import ProductId

logger: logging.Logger = logging.getLogger(__name__)

class BaseDevice(ABC):
    product_id: ProductId
    
    def __init__(self, data: int, client):
        self._data = data
        self.client = client
        self._base_data: Optional[dict] = None

    @property
    def api_endpoint(self) -> str:
        return f"{API_ENDPOINT_V2}/product/{self.product_id.value}/device/{self.device_id}/control"
    
    @abstractmethod
    async def fetch(self) -> None:
        pass
    

    @property
    def device_id(self) -> int:
        return self._data["id"]
    
    @property
    def product_id(self) -> int:
        return self._data["product_id"]
    
    @property
    def household_id(self) -> int:
        return self._data["household_id"]
    
    @property
    def name(self) -> str:
        return self._data["name"]
    
    @property
    def last_update(self) -> str:
        return self._data["last_new_event_at"]
    
    @property
    def online(self) -> bool:
        return self._data["status"]["online"]
    @property
    def battery_level(self) -> int | None:
        """Return battery level in percent."""
        return self.calculate_battery_level()

    @property
    def raw_data(self) -> Optional[dict]:
        return self._data

    def __str__(self):
        return f"<{self.__class__.__name__} id={self.device_id}>"
    

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