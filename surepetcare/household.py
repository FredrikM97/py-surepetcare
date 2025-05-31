from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_V1
from surepetcare.const import API_ENDPOINT_V2
from surepetcare.devices import load_device_class
from surepetcare.devices.pet import Pet
from surepetcare.enums import ProductId


class Household:
    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        # Add other fields as needed

    def get_pets(self):
        def parse(response):
            return [Pet(p) for p in response["data"]]

        return Command(
            method="GET", endpoint=f"{API_ENDPOINT_V1}/pet", params={"HouseholdId": self.id}, callback=parse
        )

    def get_devices(self):
        def parse(response):
            devices = []
            for device in response["data"]:
                if device["product_id"] in set(ProductId):
                    devices.append(load_device_class(device["product_id"])(device))
            return devices

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_V1}/device",
            params={"HouseholdId": self.id},
            callback=parse,
        )

    @staticmethod
    def get_households():
        def parse(response):
            return [Household(h) for h in response["data"]]

        return Command(method="GET", endpoint=f"{API_ENDPOINT_V1}/household", params={}, callback=parse)

    @staticmethod
    def get_household(household_id: int):
        return Command(method="GET", endpoint=f"{API_ENDPOINT_V1}/household/{household_id}")

    @staticmethod
    def get_product(product_id: ProductId, device_id: int):
        """TODO: Move to devices instead"""
        return Command(
            method="GET", endpoint=f"{API_ENDPOINT_V2}/product/{product_id}/device/{device_id}/control"
        )
