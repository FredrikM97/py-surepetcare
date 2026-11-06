from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterable
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from aiohttp import ClientError

from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices import load_device_class
from surepcio.devices.device import SurePetCareBase
from surepcio.devices.entities import SurePetcareResponse
from surepcio.devices.pet import Pet
from surepcio.enums import ProductId
from surepcio.security.exceptions import (
    ApiError,
    NotLoadedError,
    UnexpectedDataTypeError,
)
from surepcio.timeline import TimelineEvent, build_event_payload

if TYPE_CHECKING:
    from surepcio.client import SurePetcareClient

logger = logging.getLogger(__name__)

INITIAL_TIMELINE_LOOKBACK = timedelta(days=1)
TIMELINE_PAGE_SIZE = 25

type DevicePublisher = Callable[[SurePetCareBase], None]
type TimelinePublisher = Callable[[TimelineEvent], None]
type EventPublisher = Callable[[dict[str, Any]], None]


class Household:
    """Represents a Household."""

    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.timezone = (data.get("timezone") or {}).get("timezone")

    def get_pets(self) -> Command:
        """Get all pets in the household."""

        def chain(response: SurePetcareResponse) -> list[Command]:
            if not response.data:
                raise NotLoadedError("No data returned for get_pets()")
            if not isinstance(response.data["data"], list):
                raise UnexpectedDataTypeError("data", list, type(response.data["data"]))

            pets = [Pet(p, timezone=self.timezone) for p in response.data["data"]]
            self.data["pets"] = pets
            return [pet.refresh() for pet in pets]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/pet",
            params={"HouseholdId": self.id},
            chain=chain,
        )

    def get_devices(self) -> Command:
        """Get all devices in the household."""

        def chain(response: SurePetcareResponse) -> list[Command]:
            if not response.data:
                raise NotLoadedError("No data returned for get_devices()")
            if not isinstance(response.data["data"], list):
                raise UnexpectedDataTypeError("data", list, type(response.data["data"]))

            devices = []
            for device in response.data["data"]:
                device_cls = load_device_class(device["product_id"])
                if device_cls is not None:
                    devices.append(device_cls(device, timezone=self.timezone))
            self.data["devices"] = devices
            return [device.refresh() for device in devices]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device",
            params={"HouseholdId": self.id},
            chain=chain,
        )

    @staticmethod
    def get_households() -> Command:
        """Get all households for the user."""

        def parse(response: SurePetcareResponse) -> list[Household]:
            if not response.data:
                raise NotLoadedError("No data returned for get_households()")
            if not isinstance(response.data["data"], list):
                raise UnexpectedDataTypeError("data", list, type(response.data["data"]))

            return [Household(h) for h in response.data["data"]]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household",
            params={},
            parse=parse,
            reuse=False,
        )

    @staticmethod
    def get_household(household_id: int) -> Command:
        """Get a specific household by ID."""

        def parse(response: SurePetcareResponse) -> Household:
            if not response.data:
                raise NotLoadedError(
                    f"No data returned for get_household({household_id})"
                )
            if not isinstance(response.data["data"], dict):
                raise UnexpectedDataTypeError("data", dict, type(response.data["data"]))
            return Household(response.data["data"])

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/household/{household_id}",
            parse=parse,
            reuse=False,
        )

    @staticmethod
    def get_product(product_id: ProductId, device_id: int) -> Command:
        """Get control settings for a specific product and device ID."""

        def parse(response: SurePetcareResponse) -> dict:
            if not response.data:
                raise NotLoadedError("No data returned for get_product()")
            if not isinstance(response.data["data"], dict):
                raise UnexpectedDataTypeError("data", dict, type(response.data["data"]))
            return response.data["data"]

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/product/{product_id}/device/{device_id}/control",
            parse=parse,
            reuse=False,
        )

    def fetch_pet_device_assignments(self) -> list[Command]:
        """Return Commands to fetch assigned devices for each pet that has a matching device tag.

        This is currently the only way to map a pet to its assigned devices, as the pet API
        does not expose which devices are linked to it directly.

        Requires get_pets() and get_devices() to have been called and awaited first.
        Raises RuntimeError if pets or devices have not been loaded yet.
        """
        pets = self.data.get("pets")
        devices = self.data.get("devices")

        if pets is None:
            raise NotLoadedError(
                "Pets have not been loaded. Call and await get_pets() first."
            )
        if devices is None:
            raise NotLoadedError(
                "Devices have not been loaded. Call and await get_devices() first."
            )

        device_tag_ids: set[int] = set()
        for device in devices:
            if device.control.tags:
                for tag in device.control.tags:
                    device_tag_ids.add(tag.id)
            else:
                logger.debug(
                    "Device %s (%s) has no pet tags — skipping pet assignment lookup.",
                    device.id,
                    device.name,
                )

        commands: list[Command] = []
        for pet in pets:
            if pet.tag in device_tag_ids:
                commands.append(pet.fetch_assigned_devices())
            else:
                # Dummy to handle when pet has no assigned devices
                pet.status.devices.items = []
                pet.status.devices.count = 0

        return commands

    def get_timeline(
        self,
        since_id: int | None = None,
        before_id: int | None = None,
        page_size: int | None = None,
    ) -> Command:
        """Fetch timeline events for this household.

        Use ``since_id`` to retrieve events after a known cursor (incremental polling).
        Use ``before_id`` to page backwards through history.
        Use ``page_size`` to control how many events are returned per request (default 25).
        """

        def parse(response: SurePetcareResponse) -> list[TimelineEvent]:
            if not response.data:
                return []
            raw: list[dict] = response.data.get("data", [])
            if not isinstance(raw, list):
                raise UnexpectedDataTypeError("data", list, type(raw))
            return [TimelineEvent(**item) for item in raw]

        params: dict = {}
        if since_id is not None:
            params["since_id"] = since_id
        if before_id is not None:
            params["before_id"] = before_id
        if page_size is not None:
            params["page_size"] = page_size

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/timeline/household/{self.id}",
            params=params,
            parse=parse,
        )


class HouseholdState:
    """Refresh loaded devices and publish timeline changes without framework logic.

    Calls must be serialized by the consumer. A publisher must return successfully
    before an event is acknowledged; failures leave it eligible for retry.
    Timeline delivery is at-least-once: an incomplete event may repeat previously
    successful callbacks. Consumers should make state updates idempotent.
    """

    def __init__(
        self,
        client: SurePetcareClient,
        household: Household,
        devices: Iterable[SurePetCareBase],
        *,
        since_id: int | None = None,
        device_poll_interval: timedelta = timedelta(0),
    ) -> None:
        if device_poll_interval < timedelta(0):
            raise ValueError("Device poll interval must not be negative")
        if since_id is not None and (
            isinstance(since_id, bool) or not isinstance(since_id, int) or since_id < 0
        ):
            raise ValueError("Timeline since_id must be a non-negative integer")
        self.client = client
        self.household = household
        self.devices = {device.id: device for device in devices}
        self.device_errors: dict[int, Exception] = {}
        self.timeline_error: Exception | None = None
        # Commit the newest ID only after every page and publication succeeds.
        self._cursor: int | None = since_id
        self._seen_ids: set[int] = set()
        self._device_poll_interval = device_poll_interval.total_seconds()
        self._device_refresh_times: dict[int, float] = {}
        self._pending_device_ids: set[int] = set()

    @property
    def seen_id(self) -> int | None:
        """Newest fully acknowledged timeline ID, suitable for durable checkpoints."""
        return self._cursor

    async def refresh_device(
        self, device: SurePetCareBase, *, publish: DevicePublisher
    ) -> None:
        """Refresh one command target without fetching history or other devices."""
        try:
            await self.client.api(device.refresh())
        except (ApiError, ClientError, TimeoutError) as exc:
            if isinstance(exc, ApiError) and exc.status == 401:
                raise
            self.device_errors[device.id] = exc
            logger.warning("Device %s refresh failed: %s", device.id, exc)
        else:
            self.device_errors.pop(device.id, None)
            self._device_refresh_times[device.id] = time.monotonic()
            self._pending_device_ids.add(device.id)
            publish(device)
            self._pending_device_ids.discard(device.id)

    async def refresh(
        self,
        *,
        publish: DevicePublisher,
        publish_event: EventPublisher,
        publish_timeline: TimelinePublisher,
        on_devices_updated: Callable[[], None] | None = None,
    ) -> None:
        """Refresh device models and publish each existing timeline event.

        Consumers can evaluate initial history without emitting historical bus
        events. ``on_devices_updated`` reports completion of the device phase,
        including isolated API failures, before timeline delivery begins.
        Authentication and publication failures propagate to the caller.
        """
        await self._refresh_devices(publish)
        # Notify consumers of report availability before publishing timeline events.
        if on_devices_updated is not None:
            on_devices_updated()
        try:
            events = await self._fetch_timeline()
        except (ApiError, ClientError, TimeoutError) as exc:
            if isinstance(exc, ApiError) and exc.status == 401:
                raise
            self.timeline_error = exc
            logger.warning("Household %s timeline failed: %s", self.household.id, exc)
            return
        self.timeline_error = None
        self._publish_timeline(events, publish_timeline, publish_event)

    async def _refresh_devices(self, publish: DevicePublisher) -> None:
        """Refresh due reports, retrying pending publication of current reports."""
        for device in self.devices.values():
            last_refresh = self._device_refresh_times.get(device.id)
            if (
                device.id not in self.device_errors
                and last_refresh is not None
                and time.monotonic() - last_refresh < self._device_poll_interval
            ):
                if device.id in self._pending_device_ids:
                    publish(device)
                    self._pending_device_ids.discard(device.id)
                continue
            await self.refresh_device(device, publish=publish)

    def _publish_timeline(
        self,
        events: Iterable[TimelineEvent],
        publish_timeline: TimelinePublisher,
        publish_event: EventPublisher,
    ) -> None:
        """Deliver events in order and commit the cursor only after success."""
        newest_id = self._cursor
        for event in sorted(
            events,
            key=lambda item: (
                item.created_at or datetime.min.replace(tzinfo=UTC),
                item.id,
            ),
        ):
            if newest_id is None or event.id > newest_id:
                newest_id = event.id
            if event.id in self._seen_ids:
                continue
            payload = (
                build_event_payload(self.household.id, event)
                if self._cursor is not None
                else None
            )
            publish_timeline(event)
            if payload is not None:
                publish_event(payload)
            self._seen_ids.add(event.id)
        self._cursor = newest_id if newest_id is not None else 0
        # A committed cursor replaces the temporary acknowledgements used on retry.
        self._seen_ids.clear()

    async def _fetch_timeline(self) -> list[TimelineEvent]:
        """Collect history or incremental pages using the same pagination rules.

        Initial history includes whole boundary pages, not a strict 24-hour
        filter, so older observations can seed the consumer's current state.
        """
        cutoff = (
            datetime.now(UTC) - INITIAL_TIMELINE_LOOKBACK
            if self._cursor is None
            else None
        )
        events: dict[int, TimelineEvent] = {}
        before_id: int | None = None
        while True:
            page = await self.client.api(
                self.household.get_timeline(
                    since_id=self._cursor,
                    before_id=before_id,
                    page_size=TIMELINE_PAGE_SIZE,
                )
            )
            if not page:
                break
            events.update(
                (event.id, event)
                for event in page
                if self._cursor is None or event.id > self._cursor
            )
            oldest_id = min(event.id for event in page)
            if len(page) < TIMELINE_PAGE_SIZE or (
                cutoff is None
                and self._cursor is not None
                and oldest_id <= self._cursor
            ):
                break
            if before_id is not None and oldest_id >= before_id:
                raise ValueError("Timeline pagination returned no older events")
            if cutoff is not None and self._history_boundary_reached(page, cutoff):
                break
            before_id = oldest_id
        return list(events.values())

    def _history_boundary_reached(
        self, page: Iterable[TimelineEvent], cutoff: datetime
    ) -> bool:
        """Stop after a whole page predates the cutoff or cannot be dated."""
        newest_timestamp = max(
            (
                event.created_at
                for event in page
                if event.created_at is not None
                and event.created_at.tzinfo is not None
            ),
            default=None,
        )
        if newest_timestamp is None:
            logger.warning(
                "Household %s timeline history has no usable timestamps",
                self.household.id,
            )
            return True
        return newest_timestamp <= cutoff
