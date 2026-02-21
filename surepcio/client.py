import asyncio
import logging
from typing import Any
from typing import Union

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import RequestStatus
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
            if not command:
                logger.debug("Empty command list provided")
                return None
            results = [await self.api(cmd) for cmd in command]
            if all(result == results[-1] for result in results):
                return results[-1]
            else:
                logger.warning("Not all results are equal: %s", results)
                return results

        # If method is None, skip API call and just execute callback
        if command.method is None:
            if command.callback:
                return command.callback(None)
            return None

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

        # Extract result based on full_response flag
        result = response if command.full_response else response.data

        has_pending = (
            isinstance(response.data, dict)
            and (results := response.data.get("results", []))
            and results[0].get("request_id") is not None
            and results[0].get("status_id") not in (None, RequestStatus.COMPLETED)
        )

        # Only apply callback if not async (async will refresh device later)
        if command.callback and not has_pending:
            result = command.callback(result)

        # For async operations: poll until complete then refresh device
        if has_pending:
            await self._watcher_task(response.data, command.device)
        # For non-async PUT/POST: refresh device to get updated state
        elif command.device and command.method in ("PUT", "POST"):
            await self.api(command.device.refresh())

        return result

    async def _watcher_task(
        self, response_data: dict[Any, Any] | None, device_obj, timeout_sec: int = 30
    ) -> None:
        """Poll until the request is completed, then refresh device."""
        if not response_data or not response_data.get("results"):
            return

        logger.debug(f"Starting poll for {len(response_data['results'])} requests...")
        try:
            for attempt in range(int(timeout_sec / 2.0)):
                await asyncio.sleep(2.0)
                resp = await self.api(
                    Command(
                        method="GET",
                        endpoint=(
                            f"{API_ENDPOINT_PRODUCTION}/household/{device_obj.household_id}/"
                            "device/control/status"
                        ),
                        params={"status": [RequestStatus.PENDING]},
                        full_response=True,
                    )
                )

                data = resp.data or {}
                results = data.get("results", []) or data.get("data", [])
                if not any(r.get("status_id") == RequestStatus.PENDING for r in results):
                    logger.info("All requests completed! Refreshing device...")
                    await self.api(device_obj.refresh())
                    return

        except Exception as e:
            logger.error(f"Error polling requests: {e}")
