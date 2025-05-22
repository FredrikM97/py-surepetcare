from surepy.const import API_ENDPOINT_V1
from surepy.const import API_ENDPOINT_V2
from surepy.devices import load_device_class
from surepy.devices.base import SurepyDevice
from surepy.entities.pet import Pet
from surepy.enums import ProductId
from surepy.helper import AbstractHasGet


class HouseholdMixin(AbstractHasGet):
    async def get_household(self, household_id: int):
        return await self.get(f"{API_ENDPOINT_V1}/household/{household_id}")

    async def get_households(self):
        return (await self.get(f"{API_ENDPOINT_V1}/household"))["data"]

    async def get_devices(self, household_ids: list[int]) -> list[SurepyDevice]:
        """Get devices for a list of household IDs."""
        products = set(ProductId)

        devices = []
        for household_id in household_ids:
            household_devices = (
                await self.get(f"{API_ENDPOINT_V1}/device", params={"HouseholdId": household_id})
            )["data"]
            for device in household_devices:
                if device["product_id"] in products:
                    devices.append(load_device_class(ProductId(device["product_id"]))(self, device))

        return devices

    async def get_product(self, product_id: ProductId, device_id: int):
        return await self.get(f"{API_ENDPOINT_V2}/product/{product_id}/device/{device_id}/control")

    async def get_pets(self, household_id: int) -> list[Pet]:
        pets = []
        for pet in (await self.get(f"{API_ENDPOINT_V1}/pet", params={"HouseholdId": household_id}))["data"]:
            pets.append(Pet(self, pet))
        return pets
