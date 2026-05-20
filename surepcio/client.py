import asyncio
import logging
from typing import Any
from typing import Union

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import RequestStatus
from surepcio.security.auth import AuthClient
from surepcio.security.exceptions import ApiError

logger = logging.getLogger(__name__)


class SurePetcareClient(AuthClient):
    """SurePetcare API client. Main object to interact with the API."""

    async def _request(self, method: str, endpoint: str, **kwargs) -> SurePetcareResponse:
        await self.set_session()
        http_method = getattr(self.session, method)
        async with http_method(endpoint, **kwargs) as response:
            self.populate_headers(response)

            data = None
            if response.content_length != 0:
                try:
                    data = await response.json()
                except Exception as e:
                    logger.warning(f"Failed to parse JSON response: {e}")

            if 400 <= response.status < 600:
                raise ApiError(
                    method=method,
                    endpoint=endpoint,
                    status=response.status,
                    reason=response.reason,
                    payload=data,
                )

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

    async def api(self, command: Union[Command, list[Command]]) -> Any:
        """Execute one or more commands and normalize post-request behavior.

        Handles command lists, callback-only commands, and regular HTTP commands.
        For PUT/POST commands it also coordinates async polling and device refresh.
        """
        if command is None:
            logger.debug("No command to execute on command")
            return None
        if isinstance(command, list):
            return await self._api_list(command)

        # If method is None, skip API call and just execute callback
        if command.method is None:
            return command.callback(None) if command.callback else None

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

        is_async_operation = bool(isinstance(response.data, dict) and response.data.get("pending"))

        # Async commands are completed via watcher polling; return the raw response data.
        if is_async_operation:
            await self._watcher_task(response.data, command.device)
            return response.data

        # Synchronous PUT/POST calls refresh device state after the write completes.
        if command.device and command.method in ("PUT", "POST"):
            await self.api(command.device.refresh())

        # Callbacks receive the full SurePetcareResponse so they can inspect status/reason if needed.
        if command.callback:
            return command.callback(response)

        return response.data

    async def _api_list(self, commands: list[Command]) -> Any:
        """Execute a list of commands and collapse identical results to one value."""
        if not commands:
            logger.debug("Empty command list provided")
            return None

        results = [await self.api(cmd) for cmd in commands]
        if all(result == results[-1] for result in results):
            return results[-1]

        logger.warning("Not all results are equal: %s", results)
        return results

    async def _watcher_task(
        self,
        response_data: dict[Any, Any] | None,
        device_obj,
        timeout_sec: int = 30,
    ) -> None:
        """Poll until tracked requests are completed, then refresh device."""

        remaining_ids = self._tracked_pending_ids(response_data)
        if not remaining_ids:
            logger.debug("No pending requests to watch.")
            return

        if device_obj is None:
            logger.warning("Watcher task invoked without a device object to refresh.")
            return

        logger.info(f"Starting poll for {len(remaining_ids)} request(s): {remaining_ids}")

        async for _ in poll_with_backoff(timeout=timeout_sec):
            returned_ids = await self._poll_pending_ids(device_obj)

            # Any tracked ID missing in API response is considered completed
            completed_ids = remaining_ids - returned_ids
            remaining_ids -= completed_ids

            if completed_ids:
                logger.debug(f"Completed {len(completed_ids)} request(s): {completed_ids}")

            if not remaining_ids:
                logger.info("All tracked requests completed! Refreshing device...")
                await self.api(device_obj.refresh())
                break
        else:
            logger.warning(
                f"Watcher timed out with {len(remaining_ids)} request(s) still pending: {remaining_ids}"
            )

    @staticmethod
    def _tracked_pending_ids(response_data: dict[Any, Any] | None) -> set[str]:
        """Extract request IDs from the initial pending payload."""
        pending = response_data.get("pending") if response_data else None
        if not pending:
            return set()
        return {request_id for item in pending if (request_id := item.get("request_id"))}

    async def _poll_pending_ids(self, device_obj) -> set[str]:
        """Fetch the latest control status and return request IDs still in progress."""
        payload = await self.api(
            Command(
                method="GET",
                endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{device_obj.household_id}"
                "/device/control/status",
                params={"status": RequestStatus.not_completed()},
            )
        )

        if not isinstance(payload, dict):
            raise RuntimeError(
                "Expected control status payload to be a dict with 'data' or 'results' list entries."
            )

        if "data" in payload:
            entries = payload["data"]
        elif "results" in payload:
            entries = payload["results"]
        else:
            raise RuntimeError("Expected control status payload to include 'data' or 'results'.")

        if not isinstance(entries, list):
            raise RuntimeError("Expected control status entries to be a list.")

        return {
            request_id
            for item in entries
            if isinstance(item, dict) and (request_id := item.get("request_id"))
        }

async def poll_with_backoff(
    initial: float = 2.0, factor: float = 1.1, max_sleep: float = 10.0, timeout: float = 30.0
):
    """Yield on a growing interval until timeout is reached."""
    elapsed = 0.0
    interval = initial
    while elapsed < timeout:
        await asyncio.sleep(interval)
        yield
        elapsed += interval
        interval = min(interval * factor, max_sleep)
