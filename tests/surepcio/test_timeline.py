import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.command import Command
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import DoorDirection, DoorSide, TimelineEventType
from surepcio.security.exceptions import UnexpectedDataTypeError
from surepcio.timeline import (
    MovementResource,
    TimelineEntityInfo,
    TimelineEvent,
    build_event_payload,
)
from tests.conftest import object_snapshot


def test_get_timeline_command_params(snapshot: SnapshotAssertion) -> None:
    """get_timeline produces correct endpoint and query params."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline(since_id=42, before_id=99, page_size=10)
    object_snapshot(str(cmd), snapshot)


def test_get_timeline_command_no_params(snapshot: SnapshotAssertion) -> None:
    """get_timeline with no arguments produces empty params."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline()
    object_snapshot(str(cmd), snapshot)


def test_get_timeline_parse_empty_response(snapshot: SnapshotAssertion) -> None:
    """get_timeline parse returns empty list when response data is None."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline()
    if cmd.parse is None:
        pytest.fail("Timeline command must provide a response parser")
    result: list[TimelineEvent] = cmd.parse(SurePetcareResponse(data=None))
    object_snapshot(result, snapshot)


def test_get_timeline_parse_invalid_type() -> None:
    """get_timeline parse raises UnexpectedDataTypeError when data is not a list."""
    household = Household({"id": 7777})
    cmd: Command = household.get_timeline()
    if cmd.parse is None:
        pytest.fail("Timeline command must provide a response parser")
    with pytest.raises(UnexpectedDataTypeError):
        cmd.parse(SurePetcareResponse(data={"data": {"not": "a list"}}))


def test_build_movement_event_payload(snapshot: SnapshotAssertion) -> None:
    event = TimelineEvent(
        id=42,
        type=TimelineEventType.MOVEMENT,
        data='{"direction": "entered"}',
        movements=[
            MovementResource(
                device_id=123,
                direction=DoorDirection.ENTERED,
                side=DoorSide.INSIDE,
            )
        ],
    )

    payload = build_event_payload(7777, event)

    object_snapshot(payload, snapshot)


def test_event_preserves_supplied_resources_regardless_of_type(
    snapshot: SnapshotAssertion,
    movement_event,
) -> None:
    movement_event.event_type = TimelineEventType.LEARN_MODE
    movement_event.data = "not-json"
    payload = build_event_payload(7777, movement_event)

    object_snapshot(payload, snapshot)


def test_payload_includes_both_supplied_resource_types(movement_event, feeding_event):
    movement_event.weights = feeding_event.weights
    payload = build_event_payload(7777, movement_event)
    assert payload["movements"]
    assert payload["weights"]


def test_payload_preserves_empty_resource_collections(feeding_event):
    feeding_event.weights = []
    payload = build_event_payload(7777, feeding_event)
    assert payload["weights"] == []
    assert payload["movements"] == []


def test_payload_serializes_resource_models_directly(movement_event, feeding_event):
    movement_event.movements[0].id = 123
    movement_event.movements[0].movement_type = 2
    feeding_event.weights[0].duration = 15
    movement_event.weights = feeding_event.weights
    payload = build_event_payload(7777, movement_event)
    assert payload["movements"] == [
        resource.model_dump(mode="json") for resource in movement_event.movements
    ]
    assert payload["weights"] == [
        resource.model_dump(mode="json") for resource in movement_event.weights
    ]
    assert payload["movements"][0]["direction"] == DoorDirection.ENTERED.value
    assert payload["movements"][0]["type"] == 2
    assert "side" not in payload["movements"][0]


def test_payload_is_a_complete_event_dump(movement_event):
    movement_event.pets = [TimelineEntityInfo(id=10, name="Cat")]
    movement_event.data = '{"direction": "entered"}'
    payload = build_event_payload(7777, movement_event)
    assert payload == movement_event.model_dump(mode="json") | {"household_id": 7777}
    assert payload["type"] == TimelineEventType.MOVEMENT.value
    assert payload["data"] == movement_event.data
    assert payload["pets"] == [{"id": 10, "name": "Cat"}]
    assert "updated_at" not in payload


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["timeline", "household"]])
async def test_timeline_snapshot(
    snapshot: SnapshotAssertion, register_device_api_mocks, mock_devices
) -> None:
    """Timeline events are parsed and match the snapshot."""
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        events: list[TimelineEvent] = await client.api(household.get_timeline())

    for event in events:
        object_snapshot(event, snapshot)
