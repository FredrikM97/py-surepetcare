import logging
from typing import Any
from typing import Union

from surepcio.command import Command
from surepcio.devices.entities import SurePetcareResponse
from surepcio.security.auth import AuthClient

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient):
    """SurePetcare API client. Main object to interact with the API."""

    async def _request(self, method: str, endpoint: str, **kwargs) -> SurePetcareResponse:
        await self.set_session()
        http_method = getattr(self.session, method)
        async with http_method(endpoint, **kwargs) as response:
            self.populate_headers(response)
            if response.content_length == 0:
                return SurePetcareResponse(data=None, status=response.status, reason=response.reason)
            try:
                data = await response.json()
            except Exception:
                data = None
            return SurePetcareResponse(data=data, status=response.status, reason=response.reason)

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, headers=None
    ) -> SurePetcareResponse:
        return await self._request("get", endpoint, params=params, headers=headers)

    async def post(self, endpoint: str, params: dict | None = None, headers=None) -> SurePetcareResponse:
        return await self._request("post", endpoint, json=params, headers=headers)

    async def put(self, endpoint: str, params: dict | None = None, headers=None) -> SurePetcareResponse:
        return await self._request("put", endpoint, json=params, headers=headers)

    async def delete(self, endpoint: str, params: dict | None = None, headers=None) -> SurePetcareResponse:
        return await self._request("delete", endpoint, json=params, headers=headers)

    async def api(self, command: Union[Command, list[Command]], full_response: bool = False) -> Any:
        if command is None:
            logger.debug("No command to execute on command")
            return None
        if isinstance(command, list):
            results = [await self.api(cmd) for cmd in command]
            if all(result == results[-1] for result in results):
                return results[-1]
            else:
                logger.warning("Not all results are equal: %s", results)
                return results

        headers = self._generate_headers(headers=self.headers(command.endpoint) if command.reuse else {})
        method = command.method.lower()
        response: SurePetcareResponse = await getattr(self, method)(
            command.endpoint,
            params=command.params,
            headers=headers,
        )

        logger.debug(
            "API <%s> < %s >: status=%s, reason=%s, data=%s",
            command.method.upper(),
            command.endpoint,
            response.status,
            response.reason,
            response.data,
        )
        if command.callback:
            return command.callback(response if command.full_response else response.data)

        return response if command.full_response else response.data
