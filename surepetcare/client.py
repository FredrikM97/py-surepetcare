import logging

from surepetcare.command import Command
from surepetcare.security.auth import AuthClient

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient):
    async def get(self, endpoint: str, params: dict | None = None, headers=None) -> dict:
        await self.set_session()
        async with self.session.get(
            endpoint, params=params, headers=headers
        ) as response:
            if not response.ok:
                raise Exception(f"Error {endpoint} {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"GET {endpoint} returned 204 No Content")
                return {'status': response.status}
            if response.status == 304:
                # Not modified, keep existing data
                logger.debug(f"GET {endpoint} returned 304 Not Modified")
                return {'status': response.status}
            self.populate_headers(response)
            return {**(await response.json()), 'status': response.status}

    async def post(self, endpoint: str, data: dict | None = None, headers=None, reuse=True) -> dict:
        await self.set_session()
        async with self.session.post(
            endpoint, json=data, headers=headers
        ) as response:
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"POST {endpoint} returned 204 No Content")
                return {'status': response.status}
            self.populate_headers(response)
            return {**(await response.json()), 'status': response.status}

    async def api(self, command: Command):
        headers = self._generate_headers(headers=self.headers(command.endpoint) if command.reuse else {})
        method = command.method.lower()
        if method == "get":
            coro = self.get(
                command.endpoint, 
                params=command.params,
                headers=headers,
                )
        elif method == "post":
            coro = self.post(
                command.endpoint, 
                data=command.params,
                headers=headers,
            )

        else:
            raise NotImplementedError(f"HTTP method {command.method} not supported.")
        response = await coro

        if command.callback:
            return command.callback(response)
            
        return response