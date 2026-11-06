"""Validate explicit bowl weights from one event, without retaining observations."""

import math

from surepcio.timeline import TimelineEvent


def bowl_weights(
    event: TimelineEvent, *, device_id: int, indices: tuple[int, ...]
) -> dict[int, float]:
    """Return only supported bowl weights explicitly supplied by this event."""
    updates: dict[int, float] = {}
    for weight in event.weights:
        if weight.device_id != device_id:
            continue
        for frame in weight.frames:
            if (
                frame.index is None
                or frame.index not in indices
                or frame.current_weight is None
            ):
                continue
            if not math.isfinite(frame.current_weight):
                raise ValueError("Timeline weights must be finite")
            if frame.index in updates:
                raise ValueError("Timeline contains duplicate bowl weight readings")
            updates[frame.index] = frame.current_weight
    return updates
