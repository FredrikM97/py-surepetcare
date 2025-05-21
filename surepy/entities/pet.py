from surepy.const import API_ENDPOINT_V1, API_ENDPOINT_V2
from surepy.devices.base import BaseDevice

def requires_validation(method):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_raw_data") or self._raw_data is None:
            raise Exception("Data not fetched yet. Call fetch() first.")
        return method(self, *args, **kwargs)
    return wrapper

class Pet:
    household_id: str

    def __init__(self, client, household_id: str, pet_id:str) -> None:
        self.household_id = household_id
        self.pet_id = pet_id
        self.client = client

    @property
    def api_endpoint(self) -> str:
        return f"{API_ENDPOINT_V2}/report/household/{self.household_id}/pet/{self.pet_id}/aggregate"


    async def get_pet_dashboard(self, from_date:str, pet_ids:list):
        """Old API endpoint for fetching pet dashboard data"""
        return await self.get(f"{API_ENDPOINT_V1}/dashboard/pet", params={"From": from_date, "PetId": pet_ids})
    
    async def fetch(self, from_date, to_date) -> None:
        self._data =  await self.client.get(self.api_endpoint, params={"From": from_date, "To": to_date})
    
    @requires_validation
    def feeding(self):
        return self._data['data']['feeding']
    
    @requires_validation
    def movement(self):
        return self._data['data']['movement']
    
    @requires_validation
    def drinking(self):
        return self._data['data']['drinking']
    
    @requires_validation
    def consumption_habit(self):
        return self._data['data']['consumption_habit']
    
    @requires_validation
    def consumption_alert(self):
        return self._data['data']['consumption_alert']

    
