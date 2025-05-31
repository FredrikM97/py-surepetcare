import logging
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator


logger = logging.getLogger(__name__)


class ReportHouseholdMovementResource(BaseModel):
    """Represents a movement resource in the household report."""

    created_at: str
    updated_at: str
    deleted_at: str
    device_id: int
    tag_id: int
    user_id: int
    from_: str = Field(alias="from")
    to: str
    duration: int
    entry_device_id: int
    entry_user_id: int
    exit_device_id: int
    exit_user_id: int
    active: bool
    exit_movement_id: int
    entry_movement_id: int

    @model_validator(mode="before")
    def flatten_data(cls, values):
        # If this resource is wrapped in a 'data' key, flatten it
        if "datapoints" in values and isinstance(values["datapoints"], dict):
            if "data" in values:
                return values["data"]
            return values
        return values

    model_config = ConfigDict(extra="ignore")


class ReportWeightFrame(BaseModel):
    """Represents a weight frame in the household report."""

    index: Optional[int] = None
    weight: Optional[float] = None
    change: Optional[float] = None
    food_type_id: Optional[int] = None
    target_weight: Optional[float] = None


class ReportHouseholdFeedingResource(BaseModel):
    """Represents a feeding resource in the household report."""

    from_: str = Field(alias="from")
    to: str
    duration: int
    context: Optional[str] = None
    bowl_count: Optional[int] = None
    device_id: Optional[int] = None
    weights: Optional[list[ReportWeightFrame]] = None
    actual_weight: Optional[float] = None
    entry_user_id: Optional[int] = None
    exit_user_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    tag_id: Optional[int] = None
    user_id: Optional[int] = None

    @model_validator(mode="before")
    def flatten_data(cls, values):
        if "data" in values and isinstance(values["data"], dict):
            values = values["data"]
        # Convert context to str if it's int
        if "context" in values and not isinstance(values["context"], str):
            values["context"] = str(values["context"])
        # Convert weights to list of dicts if present
        if "weights" in values and isinstance(values["weights"], list):
            weights = []
            for w in values["weights"]:
                if isinstance(w, dict):
                    weights.append(w)
                else:
                    weights.append({"weight": w})
            values["weights"] = weights
        return values


class ReportHouseholdDrinkingResource(BaseModel):
    """Represents a drinking resource in the household report."""

    from_: str = Field(alias="from")
    to: str
    duration: int
    context: str
    bowl_count: int
    device_id: int
    weights: list[float]
    actual_weight: float
    entry_user_id: int
    exit_user_id: int
    created_at: str
    updated_at: str
    deleted_at: str
    tag_id: int
    user_id: int

    @model_validator(mode="before")
    def flatten_data(cls, values):
        if "datapoints" in values and isinstance(values["datapoints"], dict):
            if "data" in values:
                return values["data"]
            return values
        return values

    model_config = ConfigDict(extra="ignore")


class ReportHouseholdResource(BaseModel):
    pet_id: Optional[int] = None
    device_id: Optional[int] = None
    movement: Optional[list[ReportHouseholdMovementResource]] = None
    feeding: Optional[list[ReportHouseholdFeedingResource]] = None
    drinking: Optional[list[ReportHouseholdDrinkingResource]] = None

    @model_validator(mode="before")
    def flatten_datapoints(cls, values):
        for key in ["movement", "feeding", "drinking"]:
            if key in values and isinstance(values[key], dict) and "datapoints" in values[key]:
                values[key] = values[key]["datapoints"]
        return values

    model_config = ConfigDict(extra="ignore")
