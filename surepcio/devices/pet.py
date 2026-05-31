import logging
from datetime import datetime
from datetime import timezone
from typing import Optional

from pydantic import Field

from .device import PetBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.const import API_ENDPOINT_V1
from surepcio.devices.entities import DevicePetTag
from surepcio.devices.entities import SurePetcareResponse
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.security.exceptions import NotLoadedError
from surepcio.enums import ModifyDeviceTag
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


class AssignedDevices(ImprovedErrorMixin):
    """Container for assigned devices with count."""

    items: list[DevicePetTag] = Field(default_factory=list)
    count: int = 0


class LastActivity(ImprovedErrorMixin):
    """Last activity timestamp and device."""

    at: datetime
    device_id: int


class Control(ImprovedErrorMixin):
    pass


class Status(ImprovedErrorMixin):
    activity: Optional[PetPositionResource] = Field(default_factory=PetPositionResource)
    feeding: Optional[PetConsumtionResource] = Field(
        default_factory=PetConsumtionResource
    )
    drinking: Optional[PetConsumtionResource] = Field(
        default_factory=PetConsumtionResource
    )
    devices: AssignedDevices = Field(default_factory=AssignedDevices)
    last_activity: Optional[LastActivity] = None


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

    def refresh(self) -> Command:
        """Refresh the pet's activity and status data."""
        return self.fetch_report()

    def fetch_report(self) -> Command:
        def parse(response: SurePetcareResponse) -> "Pet":
            if not response.data:
                raise NotLoadedError(
                    f"No data returned for pet {self.entity_info.id} - {self.entity_info.name}"
                )
            self.status = Status(
                **{**self.status.model_dump(), **response.data["data"]["status"]}
            )
            self.status.last_activity = self.last_activity()
            return self

        return Command(
            method="GET",
            endpoint=(f"{API_ENDPOINT_PRODUCTION}/pet/{self.id}"),
            parse=parse,
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

    def last_activity(self) -> Optional[LastActivity]:
        activities = []

        # Check feeding and drinking (use 'at' field)
        for s in [self.status.feeding, self.status.drinking]:
            if s and (at := s.at) and (device_id := s.device_id):
                activities.append((at, device_id))

        # Check activity/position (uses 'since' field)
        if (
            self.status.activity
            and self.status.activity.since
            and self.status.activity.device_id
        ):
            activities.append(
                (self.status.activity.since, self.status.activity.device_id)
            )

        if not activities:
            return None

        result = max(activities, key=lambda x: x[0])
        return LastActivity(at=result[0], device_id=result[1])

    def fetch_assigned_devices(self) -> Command:
        """Fetch devices assigned to this pet."""

        def parse(response: SurePetcareResponse) -> "Pet":
            if not response.data:
                raise NotLoadedError(
                    f"No data returned for assigned devices of pet {self.id} - {self.name}"
                )
            devices_list = [
                DevicePetTag(**item) for item in response.data.get("data", [])
            ]
            self.status.devices = AssignedDevices(
                items=devices_list, count=len(devices_list)
            )
            return self

        # A 403 Forbidden response is returned by the API when the pet has no assigned devices.
        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/tag/{self.tag}/device",
            parse=parse,
        )

    def set_position(self, location: PetLocation) -> Command:
        """Set the pet's current position (inside or outside)."""

        data = {
            "where": int(location.value),
            "since": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
        return Command(
            method="POST", endpoint=f"{API_ENDPOINT_PRODUCTION}/pet/{self.id}/position", params=data,
            chain=lambda _: self.refresh()
        )

    def set_profile(self, device_id: int, profile: PetDeviceLocationProfile) -> Command:
        """Set the pet's location profile for a device (indoor only, outdoor only, etc).
        Can be used to limit access of Pet."""

        data = {
            "profile": profile.value,
        }
        available_device_ids = [tag.id for tag in self.status.devices.items]
        if device_id not in available_device_ids:
            raise ValueError(
                f"Device ID {device_id} is not assigned to pet with tag {self.tag}. \
                    Available tags: {available_device_ids}"
            )
        return Command(
            method="PUT",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{device_id}/tag/{self.tag}/async",
            params=data,
            household_id=self.household_id,
            chain=lambda _: self.fetch_assigned_devices(),
        )

    def set_tag(self, device_id: int, action: ModifyDeviceTag) -> list[Command]:
        """Add or remove a device tag on this pet.

        Add operations refresh assigned devices from the API.
        Remove operations refresh assigned devices only when another assignment should
        still remain. Removing the last assignment updates the local cache directly,
        because the API can return an error when no assignments remain.
        """

        def parse_remove(_response: SurePetcareResponse) -> "Pet":
            current_items: list[DevicePetTag] = self.status.devices.items
            filtered_items: list[DevicePetTag] = [
                item for item in current_items if item.id != device_id
            ]
            self.status.devices = AssignedDevices(
                items=filtered_items, count=len(filtered_items)
            )
            return self

        assigned_device_count: int = max(
            self.status.devices.count, len(self.status.devices.items)
        )
        should_refresh_assigned_devices: bool = (
            action == ModifyDeviceTag.ADD or assigned_device_count > 1
        )

        update_command: Command = Command(
            method=action.value,
            endpoint=f"{API_ENDPOINT_V1}/device/{device_id}/tag/{self.tag}/async",
            household_id=self.household_id,
            parse=parse_remove if not should_refresh_assigned_devices else None,
        )

        if should_refresh_assigned_devices:
            return [update_command, self.fetch_assigned_devices()]

        return [update_command]
