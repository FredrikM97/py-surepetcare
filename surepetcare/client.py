import logging

from surepetcare.command import Command
from surepetcare.entities.api import ApiResponse
from surepetcare.security.auth import AuthClient

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient, ApiResponse):
    async def get(self, endpoint: str, params: dict | None = None, headers=None) -> dict:
        if not headers:
            headers = self._generate_headers(self.token)
        await self.set_session()
        async with self.session.get(
            endpoint, params=params, headers=headers
        ) as response:
            if hasattr(self, 'populate_headers'):
                self.populate_headers(response)
            if not response.ok:
                print(response)
                raise Exception(f"Error {endpoint} {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"GET {endpoint} returned 204 No Content")
                return {}
            return await response.json()

    async def post(self, endpoint: str, data: dict | None = None, headers=None) -> dict:
        if not headers:
            headers = self._generate_headers()
        await self.set_session()
        async with self.session.post(
            endpoint, json=data, headers=headers
        ) as response:
            if hasattr(self, 'populate_headers'):
                self.populate_headers(response)
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"POST {endpoint} returned 204 No Content")
                return {}
            return await response.json()

    async def api(self, command: Command):
        method = command.method.lower()
        if method == "get":
            coro = self.get(
                command.endpoint, 
                params=command.params
                )
        elif method == "post":
            coro = self.post(
                command.endpoint, 
                data=command.params
            )

        else:
            raise NotImplementedError(f"HTTP method {command.method} not supported.")
        response = await coro
        if command.callback:
            return command.callback(response)
        return response