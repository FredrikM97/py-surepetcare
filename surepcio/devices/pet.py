import logging
from datetime import datetime
from datetime import timezone
from typing import Optional

from pydantic import Field

from .device import PetBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.entities import DevicePetTag
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import PetDeviceLocationProfile
from surepcio.enums import PetLocation
from surepcio.enums import ProductId

logger = logging.getLogger(__name__)


class PetConsumtionResource(ImprovedErrorMixin):
    """Represents a activity resource."""

    id: Optional[int] = None
    tag_id: Optional[int] = None
    device_id: Optional[int] = None
    change: Optional[list] = None
    at: Optional[datetime] = None


class PetPositionResource(ImprovedErrorMixin):
    """Represents a Position resource."""

    id: Optional[int] = None
    pet_id: Optional[int] = None
    tag_id: Optional[int] = None
    device_id: Optional[int] = None
    user_id: Optional[int] = None
    where: Optional[PetLocation] = None
    since: Optional[datetime] = None


class Control(ImprovedErrorMixin):
    pass


class Status(ImprovedErrorMixin):
    activity: Optional[PetPositionResource] = Field(default_factory=PetPositionResource)
    feeding: Optional[PetConsumtionResource] = Field(default_factory=PetConsumtionResource)
    drinking: Optional[PetConsumtionResource] = Field(default_factory=PetConsumtionResource)
    devices: Optional[list[DevicePetTag]] = None


class Pet(PetBase[Control, Status]):
    """Representation of a Pet."""

    controlCls = Control
    statusCls = Status

    def __init__(self, data: dict, **kwargs) -> None:
        super().__init__(data, **kwargs)

    @property
    def available(self) -> bool:
        """Static until figured out how to handle pet availability."""
        return True

    @property
    def photo(self) -> str | None:
        if self.entity_info.photo is None:
            return None
        return self.entity_info.photo.location

    def refresh(self) -> list[Command]:
        """Refresh the pet's report data."""
        return [self.fetch_assigned_devices(), self.fetch_report()]

    def fetch_report(self) -> Command:
        def parse(response):
            self.status = Status(**{**self.status.model_dump(), **response["data"]["status"]})
            return self

        return Command(
            method="GET",
            endpoint=(f"{API_ENDPOINT_PRODUCTION}/pet/{self.id}"),
            callback=parse,
        )

    @property
    def product(self) -> ProductId:
        return ProductId.PET

    @property
    def tag(self) -> int | None:
        if self.entity_info.tag is None:
            logger.warning("Pet tag is not set")
            return None
        return self.entity_info.tag.id

    def fetch_assigned_devices(self) -> Command:
        """Fetch devices assigned to this pet."""

        def parse(response):
            self.status.devices = [DevicePetTag(**item) for item in response["data"]]
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/tag/{self.tag}/device",
            callback=parse,
        )

    def set_position(self, location: PetLocation) -> Command:
        """Set the pet's current position (inside or outside)."""

        data = {
            "where": int(location.value),
            "since": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
        return Command(
            method="POST", endpoint=f"{API_ENDPOINT_PRODUCTION}/pet/{self.id}/position", params=data
        )

    def set_profile(self, device_id: int, profile: PetDeviceLocationProfile) -> Command:
        """Set the pet's location profile for a device (indoor only, outdoor only, etc).
        Can be used to limit access of Pet."""

        data = {
            "profile": profile.value,
        }
        available_device_ids = [tag.id for tag in self.status.devices] if self.status.devices else []
        if device_id not in available_device_ids:
            raise ValueError(
                f"Device ID {device_id} is not assigned to pet with tag {self.tag}. \
                    Available tags: {available_device_ids}"
            )
        return Command(
            method="PUT", endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{device_id}/tag/{self.tag}", params=data
        )
