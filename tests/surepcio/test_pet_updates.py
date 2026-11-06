"""The library matches raw timeline resources to pets and exposes small helpers."""

import pytest

from surepcio.entities.pet import (
    consumption_reading,
    iter_pet_events,
    last_activity_reading,
    movement_reading,
    presence_reading,
)
from surepcio.enums import DoorDirection, PetLocation, TimelineEventType
from surepcio.timeline import TimelineEntityInfo, WeightFrame


def test_pet_matching_is_event_local_and_does_not_retain_state(
    make_pet, pet_timeline_history
):
    pet = make_pet()
    for event in pet_timeline_history:
        matched = list(iter_pet_events(event, [pet]))
        if event.event_type in {
            TimelineEventType.MOVEMENT,
            TimelineEventType.FEEDING,
            TimelineEventType.POSEIDON_DRINKING,
        }:
            assert matched
            assert all(target is pet for target, _ in matched)
        else:
            assert matched == []
    assert not hasattr(pet, "_timeline")
    assert not hasattr(pet, "_observations")


def test_matching_uses_tags_and_households_without_guessing(
    make_pet, make_movement
):
    pet = make_pet()
    event = make_movement()
    assert [target.id for target, _ in iter_pet_events(event, [pet])] == [pet.id]

    event.movements[0].tag_id = 999
    assert list(iter_pet_events(event, [pet])) == []
    event.movements[0].tag_id = None
    event.pets = [TimelineEntityInfo(id=pet.id)]
    assert [target.id for target, _ in iter_pet_events(event, [pet])] == [pet.id]

    other_household_pet = make_pet(id=11, household_id=2)
    event.households = [TimelineEntityInfo(id=1)]
    assert [
        target.id for target, _ in iter_pet_events(event, [pet, other_household_pet])
    ] == [pet.id]


def test_ambiguous_tags_and_duplicate_pet_ids_are_ignored(make_pet, make_movement):
    event = make_movement()
    pet = make_pet()
    assert list(iter_pet_events(event, [pet, pet])) == []
    assert list(iter_pet_events(event, [pet, make_pet(id=11)])) == []


def test_pet_reading_helpers_transform_existing_timeline_events(
    make_pet, make_movement, make_consumption
):
    pet = make_pet()
    movement = make_movement()
    matched_movement = next(iter_pet_events(movement, [pet]))[1]
    assert movement_reading(matched_movement)[0] == PetLocation.INSIDE
    assert presence_reading(matched_movement)[0] is True
    assert last_activity_reading(matched_movement)[0] == (
        movement.movements[0].device_id
    )

    feeding = make_consumption(
        event_type=TimelineEventType.FEEDING,
        frames=[WeightFrame(index=0, change=-5.25), WeightFrame(index=1, change=-2)],
    )
    matched_feeding = next(iter_pet_events(feeding, [pet]))[1]
    reading = consumption_reading(matched_feeding)
    assert reading is not None
    assert reading[0] == 7.25
    assert last_activity_reading(matched_feeding)[0] == feeding.weights[0].device_id


@pytest.mark.parametrize(
    "frames",
    [
        [],
        [WeightFrame(index=0)],
        [WeightFrame(index=2, change=-5)],
        [WeightFrame(change=-5)],
        [WeightFrame(index=0, change=-2), WeightFrame(index=0, change=-3)],
    ],
)
def test_invalid_consumption_is_unknown(make_pet, make_consumption, frames):
    event = make_consumption(frames=frames)
    assert list(iter_pet_events(event, [make_pet()])) == []


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_consumption_is_rejected(make_pet, make_consumption, value):
    event = make_consumption(
        frames=[WeightFrame(index=0, change=value)]
    )
    with pytest.raises(ValueError, match="finite"):
        list(iter_pet_events(event, [make_pet()]))


def test_matching_validates_timestamps_and_direction(
    make_pet, make_movement, timeline_at
):
    pet = make_pet()
    assert list(iter_pet_events(make_movement(None), [pet])) == []
    with pytest.raises(ValueError, match="timezone"):
        list(iter_pet_events(make_movement(timeline_at.replace(tzinfo=None)), [pet]))
    assert list(
        iter_pet_events(
            make_movement(direction=DoorDirection.LOOKED_THROUGH), [pet]
        )
    ) == []


def test_matching_returns_timeline_event_for_the_matched_resource(
    make_pet, make_movement
):
    event = make_movement()
    matched = next(iter_pet_events(event, [make_pet()]))[1]
    assert matched is not event
    assert matched.movements == event.movements
