"""Low-level bowl matching reads explicit values without retaining device state."""

import pytest

from surepcio.devices import load_device_class
from surepcio.devices.entities import SurePetcareResponse
from surepcio.entities.bowl import bowl_weights
from surepcio.enums import BowlType, ProductId, TimelineEventType


def test_devices_do_not_retain_timeline_state():
    for product in ProductId:
        device_class = load_device_class(product)
        if device_class is None:
            continue
        device = device_class({"id": 20, "household_id": 1})
        assert not hasattr(device, "_bowl_weights")
        assert not hasattr(device, "apply_timeline")
        assert not hasattr(device, "field_definitions")


@pytest.mark.parametrize(
    ("product", "event_type"),
    [
        (ProductId.FEEDER_CONNECT, TimelineEventType.WEIGHT_CHANGED),
        (ProductId.POSEIDON_CONNECT, TimelineEventType.POSEIDON_WEIGHT_CHANGED),
    ],
)
def test_bowl_weights_are_scoped_to_matching_device_and_explicit_frames(
    product, event_type, make_weight_event
):
    device_class = load_device_class(product)
    assert device_class is not None
    device = device_class({"id": 20, "household_id": 1})
    event = make_weight_event(1, event_type=event_type, current_weight=12.25)
    assert bowl_weights(event, device_id=device.id, indices=(0,)) == {0: 12.25}
    assert bowl_weights(event, device_id=21, indices=(0,)) == {}

    event.weights[0].frames[0].current_weight = None
    assert bowl_weights(event, device_id=device.id, indices=(0,)) == {}


@pytest.mark.parametrize(
    ("invalid", "message"),
    [("duplicate", "duplicate"), ("non-finite", "finite")],
)
def test_invalid_bowl_weight_frames_are_rejected(invalid, message, make_weight_event):
    event = make_weight_event(
        1, event_type=TimelineEventType.WEIGHT_CHANGED, current_weight=12.25
    )
    extra = event.weights[0].frames[0].model_copy(deep=True)
    if invalid == "non-finite":
        extra.current_weight = float("nan")
    event.weights[0].frames.append(extra)
    with pytest.raises(ValueError, match=message):
        bowl_weights(event, device_id=event.weights[0].device_id, indices=(0,))


@pytest.mark.parametrize(
    ("product", "event_type"),
    [
        (ProductId.FEEDER_CONNECT, TimelineEventType.WEIGHT_CHANGED),
        (ProductId.POSEIDON_CONNECT, TimelineEventType.POSEIDON_WEIGHT_CHANGED),
    ],
)
def test_timeline_weights_do_not_mutate_report_state(
    product, event_type, make_weight_event
):
    device_class = load_device_class(product)
    assert device_class is not None
    device = device_class({"id": 20, "household_id": 1})
    before = device.status.model_dump()
    event = make_weight_event(1, event_type=event_type, current_weight=12.25)
    bowl_weights(event, device_id=device.id, indices=(0, 1))
    assert device.status.model_dump() == before


def test_feeder_report_processing_still_updates_bowl_state():
    device_class = load_device_class(ProductId.FEEDER_CONNECT)
    assert device_class is not None
    feeder = device_class(
        {
            "id": 20,
            "household_id": 1,
            "control": {
                "bowls": {
                    "type": BowlType.LARGE.value,
                    "settings": [{"target": 100}],
                }
            },
        }
    )
    command = feeder.refresh()
    assert command.parse is not None
    command.parse(
        SurePetcareResponse(
            data={
                "data": {
                    "status": {
                        "bowl_status": [
                            {"index": 0, "current_weight": 50, "fill_percent": 50}
                        ]
                    }
                }
            }
        )
    )
    assert feeder.status.bowl_status[0].position is not None
