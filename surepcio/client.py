import logging

from surepcio.command import Command
from surepcio.security.auth import AuthClient

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient):
    """SurePetcare API client. Main object to interact with the API."""
    async def get(self, endpoint: str, params: dict | None = None, headers=None) -> dict | None:
        """Perform a GET request to the Sure Petcare API."""
        await self.set_session()
        async with self.session.get(endpoint, params=params, headers=headers) as response:
            if not response.ok:
                raise Exception(f"Error {endpoint} {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"GET {endpoint} returned 204 No Content")
                return None
            if response.status == 304:
                # Not modified, keep existing data
                logger.info(f"GET {endpoint} returned 304 Not Modified")
                return None
            self.populate_headers(response)
            return await response.json()

    async def post(self, endpoint: str, data: dict | None = None, headers=None, reuse=True) -> dict:
        """Perform a POST request to the Sure Petcare API."""
        await self.set_session()
        async with self.session.post(endpoint, json=data, headers=headers) as response:
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"POST {endpoint} returned 204 No Content")
                return {"status": response.status}
            self.populate_headers(response)
            return await response.json()

    async def put(self, endpoint: str, data: dict | None = None, headers=None, reuse=True) -> dict:
        """Perform a PUT request to the Sure Petcare API."""
        await self.set_session()
        async with self.session.put(endpoint, json=data, headers=headers) as response:
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info("PUT {endpoint} returned 204 No Content")
                return {"status": response.status}
            logger.info(f"DELETE {endpoint} returned {response.status}")
            self.populate_headers(response)
            return await response.json()

    async def delete(self, endpoint: str, data: dict | None = None, headers=None, reuse=True) -> dict:
        """Perform a DELETE request to the Sure Petcare API."""
        await self.set_session()
        async with self.session.delete(endpoint, json=data, headers=headers) as response:
            if not response.ok:
                raise Exception(f"Error {response.status}: {await response.text()}")
            if response.status == 204:
                logger.info(f"DELETE {endpoint} returned 204 No Content")
                return {"status": response.status}
            logger.info(f"DELETE {endpoint} returned {response.status}")
            self.populate_headers(response)
            # Delete even if 200 sometimes has no content
            if response.content_length == 0:
                return {"status": response.status}

            return await response.json()

    async def api(self, command: Command):
        """Execute a Command against the Sure Petcare API."""
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
        elif method == "put":
            coro = self.put(
                command.endpoint,
                data=command.params,
                headers=headers,
            )

        elif method == "delete":
            coro = self.delete(
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
