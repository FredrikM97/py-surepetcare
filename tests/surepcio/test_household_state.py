"""Household delivery addresses fields without retaining consumer snapshots."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
import time_machine
from aiohttp import ClientConnectionError

from surepcio import Household, HouseholdState, SurePetcareClient
from surepcio.devices.pet import Pet
from surepcio.enums import DoorDirection
from surepcio.security.exceptions import ApiError, AuthenticationError
from tests.conftest import object_snapshot


@pytest.fixture(autouse=True)
def clock():
    with time_machine.travel("2026-01-02 12:00:00 +00:00", tick=False):
        yield


@pytest.fixture
def state():
    client = MagicMock(spec=SurePetcareClient)
    client.api = AsyncMock(return_value=[])
    pet = Pet(
        {
            "id": 10,
            "household_id": 1,
            "name": "Cat",
            "tag": {"id": 100, "tag": "test"},
        }
    )
    return HouseholdState(client, Household({"id": 1}), [pet])


class Consumer:
    def __init__(self):
        self.deliveries = []
        self.devices = []
        self.timeline_events = []
        self.device_phases = 0

    def device(self, device):
        self.devices.append(device.id)

    def timeline(self, event):
        self.timeline_events.append(event)

    def event(self, payload):
        self.deliveries.append({"event": payload})

    def devices_updated(self):
        self.device_phases += 1

    async def refresh(self, state):
        await state.refresh(
            publish=self.device,
            publish_event=self.event,
            publish_timeline=self.timeline,
            on_devices_updated=self.devices_updated,
        )


async def test_history_then_live_events_deliver_each_observation_in_order(
    state, snapshot, make_live_movement
):
    consumer = Consumer()
    state.client.api.return_value = [make_live_movement(10)]
    await consumer.refresh(state)
    object_snapshot(consumer.deliveries, snapshot(name="initial-history"))
    consumer.deliveries = []
    state.client.api.return_value = [
        make_live_movement(30, seconds=2),
        make_live_movement(10),
        make_live_movement(20, DoorDirection.LEFT, seconds=1),
    ]
    await consumer.refresh(state)
    object_snapshot(consumer.deliveries, snapshot(name="two-live-events"))
    consumer.deliveries = []
    await consumer.refresh(state)
    object_snapshot(
        {
            "deliveries": consumer.deliveries,
            "cursor": state._cursor,
            "seen": list(state._seen_ids),
        },
        snapshot(name="duplicate-poll"),
    )


async def test_household_publishes_the_existing_timeline_event_object(
    state, make_live_movement
):
    event = make_live_movement(10)
    state.client.api.return_value = [event]
    consumer = Consumer()
    await consumer.refresh(state)
    assert consumer.timeline_events == [event]
    assert consumer.timeline_events[0] is event


async def test_initial_history_pages_back_without_replaying_events(
    state, snapshot, make_live_movement
):
    recent = [
        make_live_movement(i, seconds=-86401 if i == 76 else 0) for i in range(76, 101)
    ]
    older = [make_live_movement(i, seconds=-(86400 + i - 50)) for i in range(51, 76)]

    def respond(command):
        if "timeline" in command.endpoint:
            return older if "before_id" in command.params else recent
        return None

    state.client.api.side_effect = respond
    consumer = Consumer()
    await consumer.refresh(state)
    assert {event.id for event in consumer.timeline_events} == set(range(51, 101))
    assert consumer.deliveries == []
    assert consumer.device_phases == 1
    object_snapshot(
        {
            "requests": [
                call.args[0].params
                for call in state.client.api.await_args_list
                if "timeline" in call.args[0].endpoint
            ],
            "events": [item for item in consumer.deliveries if isinstance(item, dict)],
            "cursor": state._cursor,
        },
        snapshot,
    )


async def test_empty_initial_history_uses_since_zero_on_subsequent_polls(state):
    consumer = Consumer()
    await consumer.refresh(state)
    assert state._cursor == 0
    state.client.api.reset_mock()
    for _ in range(3):
        await consumer.refresh(state)
    requests = [
        call.args[0].params
        for call in state.client.api.await_args_list
        if "timeline" in call.args[0].endpoint
    ]
    assert requests == [{"since_id": 0, "page_size": 25}] * 3


async def test_device_reports_poll_at_fifteen_minutes_but_timeline_every_refresh(
    state, monkeypatch
):
    monotonic = MagicMock(return_value=0)
    monkeypatch.setattr("surepcio.household.time", MagicMock(monotonic=monotonic))
    state = HouseholdState(
        state.client,
        state.household,
        state.devices.values(),
        device_poll_interval=timedelta(minutes=15),
    )
    consumer = Consumer()
    for now in (0, 300, 600, 899, 900):
        monotonic.return_value = now
        await consumer.refresh(state)
    calls = state.client.api.await_args_list
    assert len([call for call in calls if "timeline" in call.args[0].endpoint]) == 5
    assert len([call for call in calls if "/pet/" in call.args[0].endpoint]) == 2


async def test_failed_device_retries_before_interval_and_command_refresh_is_immediate(
    state, monkeypatch
):
    monotonic = MagicMock(return_value=0)
    monkeypatch.setattr("surepcio.household.time", MagicMock(monotonic=monotonic))
    state = HouseholdState(
        state.client,
        state.household,
        state.devices.values(),
        device_poll_interval=timedelta(minutes=15),
    )
    pet = next(iter(state.devices.values()))
    consumer = Consumer()
    await consumer.refresh(state)
    monotonic.return_value = 100
    state.client.api.side_effect = TimeoutError("Device failed")
    await state.refresh_device(pet, publish=consumer.device)
    assert pet.id in state.device_errors
    state.client.api.side_effect = None
    state.client.api.reset_mock()
    await consumer.refresh(state)
    assert pet.id not in state.device_errors
    assert any(
        "/pet/" in call.args[0].endpoint for call in state.client.api.await_args_list
    )
    monotonic.return_value = 200
    state.client.api.reset_mock()
    await state.refresh_device(pet, publish=consumer.device)
    assert state.client.api.await_count == 1
    monotonic.return_value = 1000
    state.client.api.reset_mock()
    await consumer.refresh(state)
    assert all(
        "timeline" in call.args[0].endpoint for call in state.client.api.await_args_list
    )


@pytest.mark.parametrize("since_id", [0, 100])
async def test_restored_cursor_never_fetches_initial_history(state, since_id):
    restored = HouseholdState(
        state.client, state.household, state.devices.values(), since_id=since_id
    )
    await Consumer().refresh(restored)
    assert restored.seen_id == since_id
    assert state.client.api.call_args.args[0].params == {
        "since_id": since_id,
        "page_size": 25,
    }


async def test_device_publication_failure_is_not_treated_as_refresh_failure(state):
    pet = next(iter(state.devices.values()))
    publish = MagicMock(side_effect=TimeoutError("Publication failed"))

    with pytest.raises(TimeoutError, match="Publication failed"):
        await state.refresh_device(pet, publish=publish)

    publish.assert_called_once_with(pet)
    assert pet.id not in state.device_errors
    assert pet.id in state._device_refresh_times
    assert pet.id in state._pending_device_ids


@pytest.mark.parametrize("expired", [False, True])
async def test_failed_model_publication_retries_without_unnecessary_api_calls(
    state, monkeypatch, expired
):
    monotonic = MagicMock(return_value=0)
    monkeypatch.setattr("surepcio.household.time", MagicMock(monotonic=monotonic))
    state = HouseholdState(
        state.client,
        state.household,
        state.devices.values(),
        since_id=0,
        device_poll_interval=timedelta(minutes=15),
    )
    pet = next(iter(state.devices.values()))
    publish = MagicMock(side_effect=TimeoutError("Publication failed"))
    for _ in range(2):
        with pytest.raises(TimeoutError, match="Publication failed"):
            await state.refresh(
                publish=publish,
                publish_event=MagicMock(),
                publish_timeline=MagicMock(),
            )
    assert state.client.api.await_count == 1
    assert state._pending_device_ids == {pet.id}

    monotonic.return_value = 900 if expired else 100
    state.client.api.reset_mock()
    consumer = Consumer()
    await consumer.refresh(state)
    assert consumer.devices == [pet.id]
    assert state.client.api.await_count == (2 if expired else 1)
    assert not state._pending_device_ids

    state.client.api.reset_mock()
    await consumer.refresh(state)
    assert consumer.devices == [pet.id]
    assert state.client.api.await_count == 1


@pytest.mark.parametrize("device_failed", [False, True])
async def test_device_phase_callback_precedes_timeline_and_events_are_payloads(
    state, make_live_movement, device_failed
):
    state = HouseholdState(
        state.client, state.household, state.devices.values(), since_id=0
    )
    event = make_live_movement(1)
    order = []

    def respond(command):
        if "timeline" in command.endpoint:
            return [event]
        if device_failed:
            raise TimeoutError("Device failed")
        return None

    state.client.api.side_effect = respond
    await state.refresh(
        publish=lambda device: order.append("device"),
        on_devices_updated=lambda: order.append("devices_updated"),
        publish_timeline=lambda event: order.append("timeline"),
        publish_event=lambda payload: order.append(payload["id"]),
    )
    assert order == (
        ["devices_updated", "timeline", 1]
        if device_failed
        else ["device", "devices_updated", "timeline", 1]
    )


@pytest.mark.parametrize("since_id", [-1, True, "100"])
def test_invalid_restored_cursor_is_rejected(state, since_id):
    with pytest.raises(ValueError, match="since_id"):
        HouseholdState(
            state.client, state.household, state.devices.values(), since_id=since_id
        )


@pytest.mark.parametrize("fail_timeline", [False, True])
async def test_failed_publication_is_retried_before_acknowledgement(
    state, snapshot, fail_timeline, make_live_movement
):
    consumer = Consumer()
    await consumer.refresh(state)
    state.client.api.return_value = [make_live_movement(1)]
    consumer.deliveries = []

    def timeline(event):
        if fail_timeline and event.id == 1:
            raise ValueError("Publication failed")
        consumer.timeline(event)

    def event(payload):
        if payload is not None:
            raise ValueError("Publication failed")

    with pytest.raises(ValueError, match="Publication failed"):
        await state.refresh(
            publish=consumer.device,
            publish_event=event,
            publish_timeline=timeline,
        )
    object_snapshot(
        {
            "seen": list(state._seen_ids),
            "cursor": state._cursor,
            "deliveries": consumer.deliveries,
        },
        snapshot(name="not-acknowledged"),
    )
    consumer.deliveries = []
    await consumer.refresh(state)
    object_snapshot(
        {
            "seen": list(state._seen_ids),
            "cursor": state._cursor,
            "deliveries": consumer.deliveries,
        },
        snapshot(name="retried"),
    )


@pytest.mark.parametrize("timeline_fails", [False, True])
@pytest.mark.parametrize(
    "failure",
    [
        ApiError("get", "endpoint", 500, "Server error"),
        ClientConnectionError("Disconnected"),
        TimeoutError("Timed out"),
    ],
)
async def test_endpoint_failure_skips_readings_and_recovers(
    state, timeline_fails, failure, caplog, snapshot
):
    def respond(command):
        if ("timeline" in command.endpoint) == timeline_fails:
            raise failure
        return []

    state.client.api.side_effect = respond
    consumer = Consumer()
    await consumer.refresh(state)
    object_snapshot(
        {
            "deliveries": consumer.deliveries,
            "device_errors": list(state.device_errors),
            "timeline_failed": state.timeline_error is failure,
            "logged": str(failure) in caplog.text,
            "initialized": state.seen_id is not None,
        },
        snapshot(name="failed"),
    )
    consumer.deliveries = []
    state.client.api.side_effect = None
    await consumer.refresh(state)
    object_snapshot(
        {
            "deliveries": consumer.deliveries,
            "device_errors": list(state.device_errors),
            "timeline_error": state.timeline_error,
            "initialized": state.seen_id is not None,
        },
        snapshot(name="recovered"),
    )


@pytest.mark.parametrize("timeline_fails", [False, True])
@pytest.mark.parametrize(
    "failure",
    [
        AuthenticationError("Expired token"),
        ApiError("get", "endpoint", 401, "Unauthorized"),
    ],
)
async def test_authentication_propagates_without_acknowledgement(
    state, timeline_fails, failure, snapshot
):
    def respond(command):
        if ("timeline" in command.endpoint) == timeline_fails:
            raise failure
        return []

    state.client.api.side_effect = respond
    with pytest.raises(type(failure)):
        await Consumer().refresh(state)
    object_snapshot(
        {
            "device_errors": list(state.device_errors),
            "timeline_error": state.timeline_error,
            "seen": list(state._seen_ids),
            "cursor": state._cursor,
        },
        snapshot,
    )


async def test_target_refresh_delivers_only_target_and_recovers(state, snapshot):
    state.devices[11] = Pet({"id": 11, "household_id": 1, "name": "Other"})
    consumer = Consumer()
    state.client.api.side_effect = TimeoutError("Target failed")
    await state.refresh_device(state.devices[10], publish=consumer.device)
    object_snapshot(
        {"deliveries": consumer.deliveries, "errors": list(state.device_errors)},
        snapshot(name="failed"),
    )
    state.client.api.side_effect = None
    await state.refresh_device(state.devices[10], publish=consumer.device)
    object_snapshot(
        {
            "deliveries": consumer.deliveries,
            "errors": list(state.device_errors),
            "requests": [
                call.args[0].endpoint for call in state.client.api.await_args_list
            ],
            "initialized": state.seen_id is not None,
        },
        snapshot(name="recovered"),
    )


async def test_processing_failure_is_not_acknowledged(
    state, monkeypatch, snapshot, make_live_movement
):
    consumer = Consumer()
    await consumer.refresh(state)
    state.client.api.return_value = [make_live_movement(1)]
    monkeypatch.setattr(
        consumer, "timeline", MagicMock(side_effect=ValueError("Bad activity"))
    )
    with pytest.raises(ValueError, match="Bad activity"):
        await consumer.refresh(state)
    object_snapshot(
        {
            "seen": list(state._seen_ids),
            "cursor": state._cursor,
        },
        snapshot,
    )


async def test_strict_cursor_skips_late_lower_id_and_releases_retry_ids(
    state, snapshot, make_live_movement, timeline_pages
):
    consumer = Consumer()
    for history in (
        [make_live_movement(10)],
        [make_live_movement(20, seconds=1)],
        [
            make_live_movement(20, seconds=1),
            make_live_movement(15, DoorDirection.LEFT, seconds=2),
        ],
    ):
        state.client.api.return_value = history
        await consumer.refresh(state)
    object_snapshot(
        {
            "cursor": state._cursor,
            "seen": list(state._seen_ids),
            "request": state.client.api.call_args.args[0].params,
            "events": [item for item in consumer.deliveries if isinstance(item, dict)],
        },
        snapshot(name="strict-cursor"),
    )
    state.client.api.return_value = [
        make_live_movement(i, seconds=i) for i in range(21, 522)
    ]
    state.client.api.side_effect = timeline_pages(state.client.api.return_value)
    await consumer.refresh(state)
    object_snapshot(
        {
            "seen_count": len(state._seen_ids),
            "cursor": state.seen_id,
        },
        snapshot(name="bounded"),
    )
    consumer.deliveries.clear()
    consumer.timeline_events.clear()
    await consumer.refresh(state)
    assert not [
        item
        for item in consumer.deliveries
        if isinstance(item, dict) and item["event"] is not None
    ]
    assert not state._seen_ids


async def test_events_at_or_below_cursor_are_not_delivered(state, make_live_movement):
    consumer = Consumer()
    state.client.api.return_value = [make_live_movement(10)]
    await consumer.refresh(state)
    consumer.deliveries.clear()
    consumer.timeline_events.clear()
    state.client.api.return_value = [
        make_live_movement(9, DoorDirection.LEFT, seconds=-1),
        make_live_movement(10),
    ]
    await consumer.refresh(state)
    assert consumer.timeline_events == []
    consumer.deliveries.clear()
    await consumer.refresh(state)
    assert consumer.timeline_events == []


async def test_equal_timestamp_events_are_delivered_in_id_order(
    state, make_live_movement
):
    consumer = Consumer()
    state.client.api.return_value = [
        make_live_movement(2, DoorDirection.LEFT),
        make_live_movement(1),
    ]
    await consumer.refresh(state)
    assert [event.id for event in consumer.timeline_events] == [1, 2]


async def test_live_poll_drains_pages_before_advancing_cursor(
    state, make_live_movement, timeline_pages
):
    consumer = Consumer()
    state.client.api.return_value = [make_live_movement(100)]
    await consumer.refresh(state)
    state.client.api.reset_mock()
    state.client.api.side_effect = timeline_pages(
        [make_live_movement(i, seconds=i) for i in range(101, 161)]
    )
    consumer.deliveries.clear()
    consumer.timeline_events.clear()
    await consumer.refresh(state)
    events = [
        item["event"]["id"]
        for item in consumer.deliveries
        if isinstance(item, dict) and item["event"] is not None
    ]
    assert events == list(range(101, 161))
    requests = [
        call.args[0].params
        for call in state.client.api.await_args_list
        if "timeline" in call.args[0].endpoint
    ]
    assert requests == [
        {"since_id": 100, "page_size": 25},
        {"since_id": 100, "before_id": 136, "page_size": 25},
        {"since_id": 100, "before_id": 111, "page_size": 25},
    ]
    assert state._cursor == 160
    state.client.api.reset_mock()
    await consumer.refresh(state)
    assert state._cursor == 160
    requests = [
        call.args[0].params
        for call in state.client.api.await_args_list
        if "timeline" in call.args[0].endpoint
    ]
    assert requests == [{"since_id": 160, "page_size": 25}]


async def test_live_pagination_failure_does_not_acknowledge_partial_pages(
    state, make_live_movement, timeline_pages
):
    consumer = Consumer()
    state.client.api.return_value = [make_live_movement(100)]
    await consumer.refresh(state)
    events = [make_live_movement(i, seconds=i) for i in range(101, 131)]
    respond = timeline_pages(events)

    def fail_second_page(command):
        if command.params.get("before_id") is not None:
            raise TimeoutError("Second page failed")
        return respond(command)

    state.client.api.side_effect = fail_second_page
    await consumer.refresh(state)
    assert state._cursor == 100
    assert not state._seen_ids
    state.client.api.side_effect = respond
    await consumer.refresh(state)
    assert not state._seen_ids


async def test_live_pagination_rejects_repeated_pages_without_advancing(
    state, make_live_movement
):
    consumer = Consumer()
    state.client.api.return_value = [make_live_movement(100)]
    await consumer.refresh(state)
    state.client.api.return_value = [
        make_live_movement(i, seconds=i) for i in range(101, 126)
    ]
    with pytest.raises(ValueError, match="pagination"):
        await consumer.refresh(state)
    assert state._cursor == 100
    assert not state._seen_ids


async def test_initial_pagination_rejects_repeated_pages_without_acknowledgement(
    state, make_live_movement
):
    state.client.api.return_value = [make_live_movement(i) for i in range(1, 26)]
    with pytest.raises(ValueError, match="pagination"):
        await Consumer().refresh(state)
    assert state.seen_id is None
    assert not state._seen_ids


async def test_partial_delivery_retries_only_unacknowledged_events(
    state, make_live_movement, timeline_pages
):
    consumer = Consumer()
    await consumer.refresh(state)
    state.client.api.side_effect = timeline_pages(
        [make_live_movement(i) for i in (1, 2, 3)]
    )
    delivered = []

    def fail_second_event(payload):
        if payload is None:
            return
        if payload["id"] == 2:
            raise ValueError("Delivery failed")
        delivered.append(payload["id"])

    with pytest.raises(ValueError, match="Delivery failed"):
        await state.refresh(
            publish=consumer.device,
            publish_event=fail_second_event,
            publish_timeline=consumer.timeline,
        )
    assert delivered == [1]
    assert state.seen_id == 0
    assert state._seen_ids == {1}

    def event(payload):
        if payload is not None:
            delivered.append(payload["id"])

    await state.refresh(
        publish=consumer.device,
        publish_event=event,
        publish_timeline=consumer.timeline,
    )
    assert delivered == [1, 2, 3]
    assert [event.id for event in consumer.timeline_events] == [1, 2, 2, 3]
    assert state.seen_id == 3
    assert not state._seen_ids
