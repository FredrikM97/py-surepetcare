import logging

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices import load_device_class
from surepcio.devices.entities import SurePetcareResponse
from surepcio.devices.pet import Pet
from surepcio.enums import ProductId
from surepcio.security.exceptions import NotLoadedError, UnexpectedDataTypeError

logger = logging.getLogger(__name__)


class Household:
    """Represents a Household."""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.timezone = (data.get("timezone") or {}).get("timezone")

    def get_pets(self) -> Command:
        """Get all pets in the household."""

        def chain(response: SurePetcareResponse) -> list[Command]:
            if not response.data:
                raise NotLoadedError("No data returned for get_pets()")
            if not isinstance(response.data["data"], list):
                raise UnexpectedDataTypeError("data", list, type(response.data["data"]))

            pets = [Pet(p, timezone=self.timezone) for p in response.data["data"]]
            self.data["pets"] = pets
            cmds: list[Command] = [pet.refresh() for pet in pets]
            # Helper for now to avoid need to manually call it
            if self.data.get("devices") is not None:
                cmds.extend(self.fetch_pet_device_assignments())
            return cmds

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/pet",
            params={"HouseholdId": self.id},
            chain=lambda response: chain(response),
        )

    def get_devices(self) -> Command:
        """Get all devices in the household."""

        def chain(response: SurePetcareResponse) -> list[Command]:
            if not response.data:
                raise NotLoadedError("No data returned for get_devices()")
            if not isinstance(response.data["data"], list):
                raise UnexpectedDataTypeError("data", list, type(response.data["data"]))

            devices = []
            for device in response.data["data"]:
                device_cls = load_device_class(device["product_id"])
                if device_cls is not None:
                    devices.append(device_cls(device, timezone=self.timezone))
            self.data["devices"] = devices
            cmds: list[Command] = [d.refresh() for d in devices]
            # Helper for now to avoid need to manually call it
            if self.data.get("pets") is not None:
                cmds.extend(self.fetch_pet_device_assignments())
            return cmds

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device",
            params={"HouseholdId": self.id},
            chain=lambda response: chain(response),
        )

    @staticmethod
    def get_households() -> Command:
        """Get all households for the user."""

        def parse(response: SurePetcareResponse) -> list["Household"]:
            if not response.data:
                raise NotLoadedError("No data returned for get_households()")
            if not isinstance(response.data["data"], list):
                raise UnexpectedDataTypeError("data", list, type(response.data["data"]))

            return [Household(h) for h in response.data["data"]]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household",
            params={},
            parse=parse,
            reuse=False,
        )

    @staticmethod
    def get_household(household_id: int) -> Command:
        """Get a specific household by ID."""

        def parse(response: SurePetcareResponse) -> "Household":
            if not response.data:
                raise NotLoadedError(f"No data returned for get_household({household_id})")
            if not isinstance(response.data["data"], dict):
                raise UnexpectedDataTypeError("data", dict, type(response.data["data"]))
            return Household(response.data["data"])

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{household_id}",
            parse=parse,
            reuse=False,
        )

    @staticmethod
    def get_product(product_id: ProductId, device_id: int) -> Command:
        """Get control settings for a specific product and device ID."""

        def parse(response: SurePetcareResponse) -> dict:
            if not response.data:
                raise NotLoadedError("No data returned for get_product()")
            if not isinstance(response.data["data"], dict):
                raise UnexpectedDataTypeError("data", dict, type(response.data["data"]))
            return response.data["data"]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/product/{product_id}/device/{device_id}/control",
            parse=parse,
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
            raise NotLoadedError("Pets have not been loaded. Call and await get_pets() first.")
        if devices is None:
            raise NotLoadedError("Devices have not been loaded. Call and await get_devices() first.")

        device_tag_ids: set[int] = set()
        for device in devices:
            if device.control.tags:
                for tag in device.control.tags:
                    device_tag_ids.add(tag.id)
            else:
                logger.debug(
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
            parse=parse,
        )
