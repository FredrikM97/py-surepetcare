import importlib
import os
import sys
from surepy.security.auth import AuthClient
from surepy.const import API_ENDPOINT_V2, API_ENDPOINT_V1
from surepy.entities.household import Household
import logging

logger = logging.getLogger(__name__)

class SurePetcareClient(AuthClient, Household):
    def __init__(self):
        super().__init__()

    async def get(self, endpoint: str, params: dict = None):
        await self.set_session()
        async with self.session.get(endpoint, params=params, headers=self._generate_headers(self.get_token())) as response:
            if not response.ok:
                print(response)
                raise Exception(f"Error {endpoint} {response.status}: {await response.text()}")
            return await response.json()

    async def post(self, endpoint: str, data: dict = None):
        await self.set_session()
        self.get_token()
        async with self.session.post(endpoint, json=data, headers=self._generate_headers(self.get_token())) as response:
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                return {}
            return await response.json()

    async def load_household(self):
        pass


    async def close(self):
        await self.close()
        await self.session.close()