import logging
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION, API_ENDPOINT_V1
from surepetcare.devices import load_device_class
from surepetcare.devices.pet import Pet
from surepetcare.enums import ProductId

logger = logging.getLogger(__name__)

class Household:
    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        # Add other fields as needed

    def get_pets(self):
        def parse(response):
            if response['status'] == 304:
                return self.data.get("pets", [])
            pets = [Pet(p) for p in response["data"]]
            self.data['pets'] = pets
            return pets
            

        return Command(
            method="GET", endpoint=f"{API_ENDPOINT_V1}/pet", params={"HouseholdId": self.id}, callback=parse
        )

    def get_devices(self):
        def parse(response):
            logger.info(f"Parsing devices for household {self.id}: {response}")
            if response['status'] == 304:
                logger.info("Returning cached devices")
                return self.data.get("devices",[])
            devices = []
            for device in response["data"]:
                if device["product_id"] in set(ProductId):
                    devices.append(load_device_class(device["product_id"])(device))
            self.data['devices'] = devices
            return devices

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device",
            params={"HouseholdId": self.id},
            callback=parse,
        )

    @staticmethod
    def get_households():
        def parse(response):
            return [Household(h) for h in response["data"]]

        return Command(method="GET", endpoint=f"{API_ENDPOINT_PRODUCTION}/household", params={}, callback=parse, reuse=False)

    @staticmethod
    def get_household(household_id: int):
        return Command(method="GET", endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{household_id}", reuse=False)

    @staticmethod
    def get_product(product_id: ProductId, device_id: int):
        """TODO: Move to devices instead"""
        return Command(
            method="GET", endpoint=f"{API_ENDPOINT_PRODUCTION}/product/{product_id}/device/{device_id}/control", reuse=False
        )
