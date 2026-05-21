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
from surepcio.security.exceptions import InvalidCommandError
from surepcio.security.exceptions import UnexpectedDataTypeError

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
            raise TypeError("api() received None — every command in a pipeline must be non-None")

        if isinstance(command, list):
            return [await self.api(cmd) for cmd in command]

        return await self.handle_command(command)

    async def handle_command(self, command: Command) -> Any:
        # reuse headers if command.reuse is True, otherwise generate new headers for this request
        headers = self._generate_headers(headers=self.headers(command.endpoint) if command.reuse else {})

        response: SurePetcareResponse = await getattr(self, command.method.lower())(
            command.endpoint,
            params=command.params,
            headers=headers,
        )

        logger.debug(
            "API <%s> < %s >: status=%s, reason=%s, data=%s",
            command.method,
            command.endpoint,
            response.status,
            response.reason,
            response.data,
        )

        # Async commands are completed via watcher polling before parse/chain executes.
        if bool(isinstance(response.data, dict) and response.data.get("pending")):
            await self._watcher_task(response.data, command.household_id)

        # parse extracts domain data from the response; chain produces follow-up Commands to execute.
        result = command.parse(response) if command.parse is not None else response
        if command.chain is not None:
            follow_up = command.chain(result)
            # In case the chain returns None,
            # we want to avoid passing that to api() which expects Command or list[Command]
            result = await self.api(follow_up) if follow_up else []

        return result

    async def _watcher_task(
        self,
        response_data: dict[Any, Any] | None,
        household_id: int | None,
        timeout_sec: int = 30,
    ) -> Any:
        """Poll until tracked requests complete, then return the refreshed device state."""
        remaining_ids = self._tracked_pending_ids(response_data)
        if not remaining_ids:
            raise ValueError("Watcher task invoked with no pending requests to watch.")
        if household_id is None:
            raise InvalidCommandError("Watcher task requires household_id to poll pending request status.")

        logger.info("Waiting for %d request(s): %s", len(remaining_ids), remaining_ids)

        async for _ in poll_with_backoff(timeout=timeout_sec):
            remaining_ids &= await self._poll_pending_ids(household_id)
            logger.debug("%d request(s) still pending", len(remaining_ids))
            if not remaining_ids:
                return
        else:
            raise TimeoutError(
                f"Watcher timed out with {len(remaining_ids)} request(s) still pending: {remaining_ids}"
            )

    @staticmethod
    def _tracked_pending_ids(response_data: dict[Any, Any] | None) -> set[str]:
        """Extract request IDs from the initial pending payload."""
        pending = response_data.get("pending") if response_data else None
        if not pending:
            return set()
        return {request_id for item in pending if (request_id := item.get("request_id"))}

    async def _poll_pending_ids(self, household_id: int) -> set[str]:
        """Fetch the latest control status and return request IDs still in progress."""

        def parse(response: SurePetcareResponse) -> set[str]:
            if not isinstance(response.data, dict):
                raise RuntimeError("Expected control status payload to be a dict.")
            data_entries = response.data.get("data")
            entries = data_entries if data_entries is not None else response.data.get("results")
            if not isinstance(entries, list):
                raise UnexpectedDataTypeError("data/results", list, type(entries))
            return {item["request_id"] for item in entries if isinstance(item, dict) and "request_id" in item}

        return await self.api(
            Command(
                method="GET",
                endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{household_id}" "/device/control/status",
                params={"status": RequestStatus.not_completed()},
                parse=parse,
            )
        )


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
