"""Convert pet timeline resources into addressed readings without retaining state."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any

from surepcio.enums import DoorDirection, PetLocation, TimelineEventType
from surepcio.timeline import MovementResource, TimelineEvent, WeightResource

if TYPE_CHECKING:
    from surepcio.devices.pet import Pet


def _consumption_changes(resource: WeightResource) -> dict[int, int | float] | None:
    changes: dict[int, int | float] = {}
    for frame in resource.frames:
        if (
            frame.index is None
            or frame.index not in (0, 1)
            or frame.index in changes
            or frame.change is None
        ):
            return None
        changes[frame.index] = frame.change
        if not math.isfinite(frame.change):
            raise ValueError("Timeline consumption must be finite")
    if not math.isfinite(sum(changes.values())):
        raise ValueError("Timeline consumption must be finite")
    return changes or None


def iter_pet_events(
    event: TimelineEvent, pets: Iterable[Pet]
) -> Iterator[tuple[Pet, TimelineEvent]]:
    """Match event-local resources to unambiguous pets in the same household."""
    at = event.created_at
    if at is None:
        return
    if at.tzinfo is None:
        raise ValueError("Timeline timestamps must include a timezone")
    if event.event_type not in {
        TimelineEventType.MOVEMENT,
        TimelineEventType.FEEDING,
        TimelineEventType.POSEIDON_DRINKING,
    }:
        return
    by_tag: dict[int, list[Pet]] = defaultdict(list)
    by_id: dict[int, list[Pet]] = defaultdict(list)
    household_ids = {item.id for item in event.households}
    for pet in pets:
        if household_ids and pet.household_id not in household_ids:
            continue
        by_id[pet.id].append(pet)
        if pet.entity_info.tag is not None:
            by_tag[pet.entity_info.tag.id].append(pet)
    resources = (
        event.movements
        if event.event_type == TimelineEventType.MOVEMENT
        else event.weights
    )
    for resource in resources:
        targets = (
            by_tag.get(resource.tag_id, [])
            if resource.tag_id is not None
            else by_id.get(event.pets[0].id, [])
            if len(event.pets) == 1
            else []
        )
        if len(targets) != 1:
            continue
        if isinstance(resource, MovementResource):
            if resource.direction not in (DoorDirection.ENTERED, DoorDirection.LEFT):
                continue
        elif _consumption_changes(resource) is None:
            continue
        yield (
            targets[0],
            event.model_copy(
                update={
                    "movements": [resource]
                    if isinstance(resource, MovementResource)
                    else [],
                    "weights": [resource]
                    if isinstance(resource, WeightResource)
                    else [],
                }
            ),
        )


def movement_reading(event: TimelineEvent) -> tuple[PetLocation, dict[str, Any]]:
    resource = event.movements[0]
    where = (
        PetLocation.INSIDE
        if resource.direction == DoorDirection.ENTERED
        else PetLocation.OUTSIDE
    )
    return (
        where,
        {
            "device_id": resource.device_id,
            "id": resource.id,
            "tag_id": resource.tag_id,
            "since": event.created_at,
            "where": where,
        },
    )


def presence_reading(event: TimelineEvent) -> tuple[bool, dict[str, Any]]:
    value, attributes = movement_reading(event)
    return (
        value == PetLocation.INSIDE,
        {key: value for key, value in attributes.items() if key != "where"},
    )


def consumption_reading(
    event: TimelineEvent,
) -> tuple[int | float, dict[str, Any]] | None:
    if event.created_at is None:
        return None
    resource = event.weights[0]
    changes = _consumption_changes(resource)
    if changes is None:
        return None
    return (
        abs(sum(changes.values())),
        {
            "device_id": resource.device_id,
            "id": resource.id,
            "tag_id": resource.tag_id,
            "at": event.created_at,
            "change_0": abs(changes.get(0, 0)),
            "change_1": abs(changes.get(1, 0)),
        },
    )


def last_activity_reading(event: TimelineEvent) -> tuple[int | None, dict[str, Any]]:
    resource = event.movements[0] if event.movements else event.weights[0]
    return (
        resource.device_id,
        {"device": resource.device_id} if resource.device_id is not None else {},
    )
