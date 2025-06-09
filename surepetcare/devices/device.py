from abc import ABC
from abc import abstractmethod
from typing import Optional

from surepetcare.command import Command
from surepetcare.entities.battery import BatteryMixin
from surepetcare.enums import ProductId


class SurepyDevice(ABC, BatteryMixin):
    def __init__(self, data: dict):
        self._data = data

        # Initialize device properties
        self._id = str(data["id"])
        self._household_id = str(data["household_id"])
        self._name = data["name"]
        self._available = data.get("status", {}).get("online", None)
        self._parent_device_id = data.get("parent_device_id", None)

    @property
    @abstractmethod
    def product(self) -> ProductId:
        raise NotImplementedError("Subclasses must implement product_id")

    @property
    def product_id(self) -> int:
        return self.product.value

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def id(self) -> int:
        return int(self._id)

    @property
    def parent_device_id(self) -> Optional[int]:
        if self._parent_device_id:
            return int(self._parent_device_id)
        return None

    @property
    def household_id(self) -> int:
        return int(self._household_id)

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def raw_data(self) -> Optional[dict]:
        return self._data

    def __str__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

    def refresh(self) -> Command:
        """Refresh the device data."""
        raise NotImplementedError("Subclasses must implement refresh method")
