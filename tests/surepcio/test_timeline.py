import json

import pytest
from pydantic import JsonValue, ValidationError
from syrupy.assertion import SnapshotAssertion

from surepcio import Household
from surepcio.client import SurePetcareClient
from surepcio.command import Command
from surepcio.devices.entities import SurePetcareResponse
from surepcio.enums import (
    DoorDirection,
    DoorSide,
    DoorStatus,
    FlapLocking,
    FoodType,
    ProductId,
    TimelineEventType,
)
from surepcio.security.exceptions import UnexpectedDataTypeError
from surepcio.timeline import (
    DoorLockingData,
    CurfewLockData,
    FeederData,
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


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            '{"weight": {"target": [198, null]}, "tare_type": null}',
            {"weight": {"target": [198, None]}, "tare_type": None},
        ),
        (
            {"direction": "entered", "side": None},
            {"direction": "entered", "side": None},
        ),
        ("null", None),
        (None, None),
        ("not-json", "not-json"),
        ('{"incomplete":', '{"incomplete":'),
        ('"text"', "text"),
        ("[0, false, null]", [0, False, None]),
        ("0", 0),
        ("false", False),
        ("{}", {}),
        ("", ""),
    ],
)
def test_timeline_data_is_decoded(data, expected, snapshot: SnapshotAssertion) -> None:
    event = TimelineEvent(id=42, type=TimelineEventType.LEARN_MODE, data=data)
    payload = build_event_payload(7777, event)

    assert type(event.data) is type(expected)
    if expected is not None:
        assert type(payload["data"]) is type(expected)
    object_snapshot({"internal_data": event.data, "published_payload": payload}, snapshot)


def test_payload_preserves_unknown_event_type_and_data(
    snapshot: SnapshotAssertion,
) -> None:
    event = TimelineEvent(id=42)
    payload = build_event_payload(7777, event)

    assert payload == event.model_dump(exclude_none=False, exclude_unset=True) | {
        "household_id": 7777
    }
    object_snapshot({"internal_model": event, "published_payload": payload}, snapshot)


def test_payload_distinguishes_absent_and_explicit_empty_values(
    snapshot: SnapshotAssertion,
) -> None:
    absent = TimelineEvent(id=42)
    explicit = TimelineEvent(id=43, data=None, movements=[], weights=[])
    object_snapshot(
        {
            "absent": build_event_payload(7777, absent),
            "explicit": build_event_payload(7777, explicit),
        },
        snapshot,
    )
    assert absent.movements == explicit.movements
    assert absent.data is explicit.data


def test_payload_preserves_empty_collections_inside_data(
    snapshot: SnapshotAssertion,
) -> None:
    event = TimelineEvent(
        id=42,
        type=TimelineEventType.CURFEW_LOCK_STATUS,
        data={"curfew": [], "locked": False, "mode": 0},
    )
    object_snapshot(build_event_payload(7777, event), snapshot)


@pytest.mark.parametrize("mode", list(FlapLocking))
def test_locking_data_serializes_mode_names(
    mode: FlapLocking, snapshot: SnapshotAssertion
) -> None:
    event = TimelineEvent(
        id=42,
        type=TimelineEventType.DOOR_LOCKING_MODE,
        data={"mode": mode.value, "last_mode": mode.value, "curfew": [], "locked": False},
    )
    original_data = event.data
    assert isinstance(event.data, DoorLockingData)
    assert event.data.mode is mode
    assert event.data.last_mode is mode
    object_snapshot(
        {"internal_data": event.data, "published_payload": build_event_payload(7777, event)},
        snapshot,
    )
    assert event.data is original_data


@pytest.mark.parametrize(
    "data", [None, "text", {}, {"mode": None}, {"last_mode": None}]
)
def test_locking_data_preserves_missing_modes(data, snapshot: SnapshotAssertion) -> None:
    event = TimelineEvent(id=42, type=TimelineEventType.DOOR_LOCKING_MODE, data=data)
    object_snapshot(build_event_payload(7777, event), snapshot)


@pytest.mark.parametrize("field", ["mode", "last_mode"])
def test_locking_data_rejects_undefined_modes(field: str) -> None:
    with pytest.raises(ValidationError):
        TimelineEvent(
            id=42, type=TimelineEventType.DOOR_LOCKING_MODE, data={field: 999}
        )


@pytest.mark.parametrize("encoded", [False, True])
def test_locking_data_preserves_additional_api_fields(
    encoded: bool, snapshot: SnapshotAssertion
) -> None:
    data: dict[str, JsonValue] = {
        "mode": 0,
        "last_mode": None,
        "simulated_api_extension": {"enabled": False, "count": 0, "items": [], "value": None},
    }
    event = TimelineEvent(
        id=42,
        type=TimelineEventType.DOOR_LOCKING_MODE,
        data=json.dumps(data) if encoded else data,
    )
    assert isinstance(event.data, DoorLockingData)
    object_snapshot(build_event_payload(7777, event), snapshot)


def test_other_event_modes_remain_numeric(snapshot: SnapshotAssertion) -> None:
    event = TimelineEvent(
        id=42, type=TimelineEventType.TRAINING_MODE, data={"mode": 1, "last_mode": 0}
    )
    assert isinstance(event.data, dict)
    object_snapshot(build_event_payload(7777, event), snapshot)


@pytest.mark.parametrize(
    "event_type", [TimelineEventType.FEEDING, TimelineEventType.WEIGHT_CHANGED]
)
@pytest.mark.parametrize("encoded", [False, True])
def test_feeder_data_is_typed(
    event_type: TimelineEventType, encoded: bool, snapshot: SnapshotAssertion
) -> None:
    data: dict[str, JsonValue] = {
        "encounter_source": None,
        "weight": {
            "count": 1,
            "food_type": [2, None],
            "plate": {"half": 21.9, "full": 54.3},
            "bowl": {"half": 31.3, "full": 57.18},
            "target": [198, 0],
            "tare_value": None,
        },
        "tare_type": None,
    }
    event = TimelineEvent(
        id=42, type=event_type, data=json.dumps(data) if encoded else data
    )
    assert isinstance(event.data, FeederData)
    assert event.data.weight is not None
    assert event.data.weight.plate is not None
    assert event.data.weight.food_type is not None
    assert event.data.weight.food_type[0] is FoodType.DRY
    object_snapshot(
        {"internal_model": event, "published_payload": build_event_payload(7777, event)},
        snapshot,
    )


def test_feeder_data_preserves_simulated_api_extensions(
    snapshot: SnapshotAssertion,
) -> None:
    """Exercise forward compatibility separately from real API-shaped inputs."""
    event = TimelineEvent(
        id=42,
        type=TimelineEventType.FEEDING,
        data={
            "simulated_api_extension": 0,
            "weight": {
                "simulated_api_extension": {"items": [], "enabled": False},
                "plate": {"simulated_api_extension": None},
            },
        },
    )
    object_snapshot(build_event_payload(7777, event), snapshot)


def test_curfew_data_is_typed(snapshot: SnapshotAssertion) -> None:
    event = TimelineEvent(
        id=42,
        type=TimelineEventType.CURFEW_LOCK_STATUS,
        data='{"mode":null,"locked":true,"time":"10:36","lock":"10:36","unlock":"19:16"}',
    )
    assert isinstance(event.data, CurfewLockData)
    object_snapshot(
        {"internal_model": event, "published_payload": build_event_payload(7777, event)},
        snapshot,
    )


@pytest.mark.parametrize(
    ("event_type", "data"),
    [
        (TimelineEventType.FEEDING, {"weight": {"food_type": [999]}}),
        (TimelineEventType.FEEDING, {"weight": {"plate": {"half": "invalid"}}}),
        (TimelineEventType.WEIGHT_CHANGED, {"weight": "invalid"}),
        (TimelineEventType.CURFEW_LOCK_STATUS, {"locked": "invalid"}),
    ],
)
def test_typed_data_rejects_invalid_known_fields(event_type, data) -> None:
    with pytest.raises(ValidationError):
        TimelineEvent(id=42, type=event_type, data=data)


@pytest.mark.parametrize(
    "event_type",
    [
        TimelineEventType.FEEDING,
        TimelineEventType.WEIGHT_CHANGED,
        TimelineEventType.CURFEW_LOCK_STATUS,
    ],
)
def test_typed_data_omits_unprovided_fields(
    event_type: TimelineEventType, snapshot: SnapshotAssertion
) -> None:
    object_snapshot(
        build_event_payload(7777, TimelineEvent(id=42, type=event_type, data={})), snapshot
    )


def test_event_preserves_supplied_resources_regardless_of_type(
    snapshot: SnapshotAssertion,
    movement_event,
) -> None:
    movement_event.event_type = TimelineEventType.LEARN_MODE
    movement_event.data = "not-json"
    payload = build_event_payload(7777, movement_event)

    object_snapshot(payload, snapshot)


def test_payload_includes_both_supplied_resource_types(
    movement_event, feeding_event, snapshot: SnapshotAssertion
) -> None:
    movement_event.weights = feeding_event.weights
    payload = build_event_payload(7777, movement_event)
    object_snapshot(payload, snapshot)


def test_payload_preserves_empty_resource_collections(
    feeding_event, snapshot: SnapshotAssertion
) -> None:
    feeding_event.weights = []
    payload = build_event_payload(7777, feeding_event)
    object_snapshot(
        {"internal_model": feeding_event, "published_payload": payload}, snapshot
    )


@pytest.mark.parametrize("field", ["households", "devices", "pets", "tags", "users"])
def test_payload_serializes_product_ids_in_every_reference_collection(
    field: str, snapshot: SnapshotAssertion
) -> None:
    event = TimelineEvent.model_validate(
        {
            "id": 42,
            "type": TimelineEventType.NEW_DEVICE,
            field: [
                {"id": 100, "product_id": ProductId.HUB.value},
                {"id": 101, "product_id": ProductId.FEEDER_CONNECT.value},
            ],
        }
    )
    object_snapshot(build_event_payload(7777, event), snapshot)


@pytest.mark.parametrize("direction", list(DoorDirection))
def test_movement_direction_serializes_as_name(
    direction: DoorDirection, snapshot: SnapshotAssertion
) -> None:
    movement = MovementResource(direction=direction)
    object_snapshot(movement.model_dump(mode="json"), snapshot)
    assert movement.direction is direction
    assert movement.model_dump()["direction"] is direction


@pytest.mark.parametrize("side", list(DoorSide))
def test_movement_side_serializes_as_name(
    side: DoorSide, snapshot: SnapshotAssertion
) -> None:
    movement = MovementResource(side=side)
    object_snapshot(movement.model_dump(mode="json"), snapshot)
    assert movement.side is side
    assert movement.model_dump()["side"] is side


@pytest.mark.parametrize("product", list(ProductId))
def test_reference_product_serializes_as_name(
    product: ProductId, snapshot: SnapshotAssertion
) -> None:
    reference = TimelineEntityInfo.model_validate(
        {"id": 42, "product_id": product.value}
    )
    object_snapshot(reference.model_dump(mode="json"), snapshot)
    assert reference.product_id is product
    assert reference.model_dump()["product_id"] is product


@pytest.mark.parametrize("status", list(DoorStatus))
def test_movement_status_serializes_as_name(
    status: DoorStatus, snapshot: SnapshotAssertion
) -> None:
    movement = MovementResource.model_validate({"type": status.value})
    assert movement.movement_type is status
    assert movement.model_dump()["type"] is status
    object_snapshot(movement.model_dump(mode="json"), snapshot)


def test_movement_status_rejects_unknown_and_preserves_missing_codes(
    snapshot: SnapshotAssertion,
) -> None:
    with pytest.raises(ValidationError) as error:
        MovementResource.model_validate({"type": 999})
    missing = MovementResource()
    assert missing.movement_type is None
    object_snapshot(
        {
            "unknown_error": [
                {"loc": item["loc"], "type": item["type"], "input": item["input"]}
                for item in error.value.errors()
            ],
            "missing": missing.model_dump(mode="json"),
            "including_none": missing.model_dump(mode="json", exclude_none=False),
        },
        snapshot,
    )


def test_reference_rejects_unknown_and_preserves_missing_product_ids(
    snapshot: SnapshotAssertion,
) -> None:
    with pytest.raises(ValidationError) as error:
        TimelineEntityInfo.model_validate({"id": 42, "product_id": 999})
    missing = TimelineEntityInfo(id=42)
    assert missing.product_id is None
    object_snapshot(
        {
            "unknown_error": [
                {"loc": item["loc"], "type": item["type"], "input": item["input"]}
                for item in error.value.errors()
            ],
            "missing": missing.model_dump(mode="json"),
            "including_none": missing.model_dump(mode="json", exclude_none=False),
        },
        snapshot,
    )


def test_unknown_movement_direction_remains_none(snapshot: SnapshotAssertion) -> None:
    movement = MovementResource()
    assert movement.direction is None
    object_snapshot(
        {
            "default": movement.model_dump(mode="json"),
            "including_none": movement.model_dump(mode="json", exclude_none=False),
        },
        snapshot,
    )


def test_payload_serializes_resource_models_directly(
    movement_event, feeding_event, snapshot: SnapshotAssertion
) -> None:
    movement_event.movements[0].id = 123
    movement_event.movements[0].movement_type = DoorStatus.STATUS_6
    feeding_event.weights[0].duration = 15
    movement_event.weights = feeding_event.weights
    payload = build_event_payload(7777, movement_event)
    assert payload["movements"] == [
        resource.model_dump(exclude_none=False, exclude_unset=True)
        for resource in movement_event.movements
    ]
    assert payload["weights"] == [
        resource.model_dump(exclude_none=False, exclude_unset=True)
        for resource in movement_event.weights
    ]
    object_snapshot(payload, snapshot)


def test_payload_preserves_event_fields_with_readable_type(
    movement_event, snapshot: SnapshotAssertion
) -> None:
    movement_event.pets = [TimelineEntityInfo(id=10, name="Cat")]
    movement_event.data = {"direction": "entered"}
    payload = build_event_payload(7777, movement_event)
    assert payload == movement_event.model_dump(
        exclude_none=False, exclude_unset=True
    ) | {
        "household_id": 7777
    }
    assert movement_event.event_type is TimelineEventType.MOVEMENT
    assert payload["type"] is TimelineEventType.MOVEMENT
    assert movement_event.model_dump()["type"] is TimelineEventType.MOVEMENT
    object_snapshot(payload, snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["timeline", "household"]])
@pytest.mark.parametrize("snapshot_view", ["internal_model", "published_payload"])
async def test_timeline_snapshot(
    snapshot: SnapshotAssertion,
    register_device_api_mocks,
    mock_devices,
    snapshot_view: str,
) -> None:
    """Snapshot typed API models and user-facing payloads under distinct names."""
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        events: list[TimelineEvent] = await client.api(household.get_timeline())

    for event in events:
        if snapshot_view == "internal_model":
            object_snapshot(event, snapshot)
        else:
            object_snapshot(build_event_payload(household.id, event), snapshot)
