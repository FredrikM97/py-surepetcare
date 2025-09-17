import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.const import API_ENDPOINT_V1
from surepcio.const import API_ENDPOINT_V2
from surepcio.devices import load_device_class
from surepcio.devices.pet import Pet
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Household:
    """Represents a Household."""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.timezone = (data.get("timezone") or {}).get("timezone")

    def get_pets(self):
        """Get all pets in the household."""

        def parse(response):
            if not response:
                return self.data.get("pets", [])
            pets = [Pet(p, timezone=self.timezone) for p in response["data"]]
            self.data["pets"] = pets
            return pets

        return Command(
            method="GET", endpoint=f"{API_ENDPOINT_V1}/pet", params={"HouseholdId": self.id}, callback=parse
        )

    def get_devices(self):
        """Get all devices in the household."""

        def parse(response):
            if not response:
                logger.info("Returning cached devices")
                return self.data.get("devices", [])
            if isinstance(response["data"], list):
                devices = []
                for device in response["data"]:
                    if device["product_id"] in set(ProductId):
                        devices.append(
                            load_device_class(device["product_id"])(device, timezone=self.timezone)
                        )
                self.data["devices"] = devices
                return devices
            return []

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device",
            params={"HouseholdId": self.id},
            callback=parse,
        )

    @staticmethod
    def get_households():
        """Get all households for the user."""

        def parse(response):
            if not response:
                return []
            if isinstance(response["data"], list):
                return [Household(h) for h in response["data"]]
            return []

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household",
            params={},
            callback=parse,
            reuse=False,
        )

    @staticmethod
    def get_household(household_id: int):
        """Get a specific household by ID."""

        def parse(response):
            if not response:
                return None
            if isinstance(response["data"], dict):
                return Household(response["data"])
            return {}

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{household_id}",
            callback=parse,
            reuse=False,
        )

    @staticmethod
    def get_product(product_id: ProductId, device_id: int):
        """Get control settings for a specific product and device ID."""

        def parse(response):
            if not response:
                return None
            if isinstance(response["data"], dict):
                return response["data"]
            return {}

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V2}/product/{product_id}/device/{device_id}/control",
            callback=parse,
            reuse=False,
        )
