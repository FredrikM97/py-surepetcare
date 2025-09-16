import logging
from datetime import datetime
from typing import Optional

from pydantic import Field

from .device import PetBase
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.entities.error_mixin import ImprovedErrorMixin
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
    where: Optional[int] = None
    since: Optional[datetime] = None


class Control(ImprovedErrorMixin):
    pass


class Status(ImprovedErrorMixin):
    activity: Optional[PetPositionResource] = Field(default_factory=PetPositionResource)
    feeding: Optional[PetConsumtionResource] = Field(default_factory=PetConsumtionResource)
    drinking: Optional[PetConsumtionResource] = Field(default_factory=PetConsumtionResource)


class Pet(PetBase[Control, Status]):
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
        """Refresh the pet's report data."""
        return self.fetch_report()

    def fetch_report(self) -> Command:
        def parse(response):
            self.status = Status(**response["data"]["status"])
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
