import logging

from surepetcare.security.auth import AuthClient

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient):
    async def get(self, endpoint: str, params: dict | None = None):
        await self.set_session()
        async with self.session.get(
            endpoint, params=params, headers=self._generate_headers(self.token)
        ) as response:
            if not response.ok:
                print(response)
                raise Exception(f"Error {endpoint} {response.status}: {await response.text()}")
            return await response.json()

    async def post(self, endpoint: str, data: dict | None = None):
        await self.set_session()
        async with self.session.post(
            endpoint, json=data, headers=self._generate_headers(self.token)
        ) as response:
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                return {}
            return await response.json()

    async def api(self, command):
        method = command.method.lower()
        if method == "get":
            response = await self.get(command.endpoint, params=command.params)
        elif method == "post":
            response = await self.post(command.endpoint, data=command.params)
        else:
            raise NotImplementedError(f"HTTP method {command.method} not supported.")
        if command.callback:
            return command.callback(response)
        return response
