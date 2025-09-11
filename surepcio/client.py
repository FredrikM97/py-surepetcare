import logging

from surepcio.command import Command
from surepcio.security.auth import AuthClient

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient):
    async def get(self, endpoint: str, params: dict | None = None, headers=None) -> dict | None:
        await self.set_session()
        async with self.session.get(endpoint, params=params, headers=headers) as response:
            if not response.ok:
                raise Exception("Error %s %s: %s", endpoint, response.status, await response.text())
            if response.status == 204:
                logger.info("GET %s returned 204 No Content", endpoint)
                return None
            if response.status == 304:
                # Not modified, keep existing data
                logger.debug("GET %s returned 304 Not Modified", endpoint)
                return None
            self.populate_headers(response)
            return await response.json()

    async def post(self, endpoint: str, data: dict | None = None, headers=None, reuse=True) -> dict:
        await self.set_session()
        async with self.session.post(endpoint, json=data, headers=headers) as response:
            if not response.ok:
                raise Exception("Error %s: %s", response.status, await response.text())
            if response.status == 204:
                logger.info("POST %s returned 204 No Content", endpoint)
                return {"status": 204}
            self.populate_headers(response)
            return await response.json()

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
            raise NotImplementedError("HTTP method %s not supported.", command.method)
        response = await coro

        logger.debug("Response for %s refresh: %s", command.endpoint, response)
        if command.callback:
            return command.callback(response)

        return response
