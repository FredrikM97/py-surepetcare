"""Reusable library timeline setup; tests own event application and assertions."""

from datetime import UTC, datetime, timedelta

import pytest

from surepcio import SurePetcareClient, TimelineEvent
from surepcio.command import Command
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.devices.pet import Pet
from surepcio.devices.poseidon_connect import PoseidonConnect
from surepcio.enums import DoorDirection, PetLocation, TimelineEventType
from surepcio.timeline import MovementResource, WeightFrame, WeightResource

TIMELINE_AT = datetime(2026, 1, 1, 12, tzinfo=UTC)


@pytest.fixture
def timeline_at() -> datetime:
    return TIMELINE_AT


@pytest.fixture
def timeline_client() -> SurePetcareClient:
    return SurePetcareClient()


@pytest.fixture
def bowl_device(device_type: type[FeederConnect] | type[PoseidonConnect]):
    return device_type({"id": 20, "name": "Bowl", "household_id": 1})


@pytest.fixture
def make_pet():
    def create(id: int = 10, tag_id: int = 100, household_id: int = 1) -> Pet:
        return Pet(
            {
                "id": id,
                "household_id": household_id,
                "name": "Cat",
                "tag": {"id": tag_id, "tag": "test"},
                "activity": {"where": PetLocation.OUTSIDE.value},
                "feeding": {"change": [100, 100]},
                "drinking": {"change": [100, 100]},
            }
        )

    return create


@pytest.fixture
def make_movement():
    def create(
        at: datetime | None = TIMELINE_AT,
        direction: DoorDirection = DoorDirection.ENTERED,
        tag_id: int | None = 100,
        event_id: int = 1,
    ) -> TimelineEvent:
        return TimelineEvent(
            id=event_id,
            type=TimelineEventType.MOVEMENT,
            created_at=at,
            movements=[
                MovementResource(tag_id=tag_id, device_id=20, direction=direction)
            ],
        )

    return create


@pytest.fixture
def make_consumption():
    def create(
        at: datetime | None = TIMELINE_AT,
        *,
        event_type: TimelineEventType = TimelineEventType.FEEDING,
        frames: list[WeightFrame] | None = None,
        tag_id: int | None = 100,
        event_id: int = 2,
        device_id: int = 30,
    ) -> TimelineEvent:
        return TimelineEvent(
            id=event_id,
            type=event_type,
            created_at=at,
            weights=[
                WeightResource(
                    tag_id=tag_id,
                    device_id=device_id,
                    frames=frames
                    if frames is not None
                    else [
                        WeightFrame(index=1, change=-2),
                        WeightFrame(index=0, change=-5),
                    ],
                )
            ],
        )

    return create


@pytest.fixture
def movement_event(make_movement) -> TimelineEvent:
    return make_movement()


@pytest.fixture
def feeding_event(make_consumption) -> TimelineEvent:
    return make_consumption(frames=[WeightFrame(index=0, change=-7)])


@pytest.fixture
def drinking_event(make_consumption) -> TimelineEvent:
    return make_consumption(
        event_type=TimelineEventType.POSEIDON_DRINKING,
        event_id=3,
        device_id=40,
        frames=[WeightFrame(index=0, change=-5)],
    )


@pytest.fixture
def pet_timeline_history(
    movement_event, feeding_event, drinking_event
) -> list[TimelineEvent]:
    return [movement_event, feeding_event, drinking_event]


@pytest.fixture
def make_live_movement(make_movement):
    def create(
        event_id: int,
        direction: DoorDirection = DoorDirection.ENTERED,
        *,
        seconds: int = 0,
    ) -> TimelineEvent:
        return make_movement(
            at=datetime.now(UTC) + timedelta(seconds=seconds),
            direction=direction,
            event_id=event_id,
        )

    return create


@pytest.fixture
def timeline_pages():
    """Emulate the API's ID bounds and page-size limit for realistic live polling."""

    def create(events: list[TimelineEvent]):
        def respond(command: Command):
            if "timeline" not in command.endpoint:
                return None
            since_id = command.params.get("since_id")
            before_id = command.params.get("before_id")
            matching = [
                event
                for event in events
                if (since_id is None or event.id > since_id)
                and (before_id is None or event.id < before_id)
            ]
            return sorted(matching, key=lambda event: event.id, reverse=True)[
                : command.params.get("page_size", 25)
            ]

        return respond

    return create


@pytest.fixture
def make_weight_event():
    def create(
        event_id: int,
        *,
        event_type: TimelineEventType = TimelineEventType.WEIGHT_CHANGED,
        seconds: int = 0,
        device_id: int = 20,
        household_id: int = 1,
        index: int = 0,
        current_weight: float | None = None,
        change: float | None = None,
    ) -> TimelineEvent:
        return TimelineEvent(
            id=event_id,
            type=event_type,
            created_at=TIMELINE_AT + timedelta(seconds=seconds),
            households=[{"id": household_id}],
            weights=[
                WeightResource(
                    device_id=device_id,
                    frames=[
                        WeightFrame(
                            index=index, current_weight=current_weight, change=change
                        )
                    ],
                )
            ],
        )

    return create
