import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices import load_device_class
from surepcio.devices.entities import SurePetcareResponse
from surepcio.devices.pet import Pet
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class Household:
    """Represents a Household."""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.timezone = (data.get("timezone") or {}).get("timezone")

    def get_pets(self) -> Command:
        """Get all pets in the household."""

        def parse(response: SurePetcareResponse):
            if not response.data:
                return self.data.get("pets", [])
            pets = [Pet(p, timezone=self.timezone) for p in response.data["data"]]
            self.data["pets"] = pets
            return pets

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/pet",
            params={"HouseholdId": self.id},
            callback=parse,
        )

    def get_devices(self) -> Command:
        """Get all devices in the household."""

        def parse(response: SurePetcareResponse):
            if not response.data:
                logger.info("Returning cached devices")
                return self.data.get("devices", [])
            if isinstance(response.data["data"], list):
                devices = []
                for device in response.data["data"]:
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
    def get_households() -> Command:
        """Get all households for the user."""

        def parse(response: SurePetcareResponse):
            if not response.data:
                return []
            if isinstance(response.data["data"], list):
                return [Household(h) for h in response.data["data"]]
            return []

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household",
            params={},
            callback=parse,
            reuse=False,
        )

    @staticmethod
    def get_household(household_id: int) -> Command:
        """Get a specific household by ID."""

        def parse(response: SurePetcareResponse):
            if not response.data:
                return None
            if isinstance(response.data["data"], dict):
                return Household(response.data["data"])
            return {}

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{household_id}",
            callback=parse,
            reuse=False,
        )

    @staticmethod
    def get_product(product_id: ProductId, device_id: int) -> Command:
        """Get control settings for a specific product and device ID."""

        def parse(response: SurePetcareResponse):
            if not response.data:
                return None
            if isinstance(response.data["data"], dict):
                return response.data["data"]
            return {}

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/product/{product_id}/device/{device_id}/control",
            callback=parse,
            reuse=False,
        )

    def fetch_pet_device_assignments(self) -> list[Command]:
        """Return Commands to fetch assigned devices for each pet that has a matching device tag.

        This is currently the only way to map a pet to its assigned devices, as the pet API
        does not expose which devices are linked to it directly.

        Requires get_pets() and get_devices() to have been called and awaited first.
        Raises RuntimeError if pets or devices have not been loaded yet.
        """
        pets = self.data.get("pets")
        devices = self.data.get("devices")

        if pets is None:
            raise RuntimeError("Pets have not been loaded. Call and await get_pets() first.")
        if devices is None:
            raise RuntimeError("Devices have not been loaded. Call and await get_devices() first.")

        device_tag_ids: set[int] = set()
        for device in devices:
            if device.control.tags:
                for tag in device.control.tags:
                    device_tag_ids.add(tag.id)
            else:
                logger.warning(
                    "Device %s (%s) has no pet tags — skipping pet assignment lookup.",
                    device.id,
                    device.name,
                )

        return [pet.fetch_assigned_devices() for pet in pets if pet.tag in device_tag_ids]

    def get_timeline(self, since_id: int | None = None, before_id: int | None = None) -> Command:
        def parse(response: SurePetcareResponse):
            if not response.data:
                return []
            return response.data.get("data", [])

        params = {}
        if since_id is not None:
            params["since_id"] = since_id
        if before_id is not None:
            params["before_id"] = before_id

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/timeline/household/{self.id}",
            params=params,
            callback=parse,
        )