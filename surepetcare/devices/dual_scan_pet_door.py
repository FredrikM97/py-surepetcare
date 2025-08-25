import logging

from .device import BaseControl
from .device import BaseStatus
from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId

logger = logging.getLogger(__name__)


class DualScanPetDoor(SurepyDevice):
    def __init__(self, data: dict) -> None:
        try:
            super().__init__(data)
            self.status: BaseStatus = BaseStatus(**data)
            self.control: BaseControl = BaseControl(**data)
        except Exception as e:
            logger.warning("Error while storing data %s", data)
            raise e

    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_PET_DOOR

    def refresh(self):
        def parse(response):
            if not response:
                return self
            self.status = BaseStatus(**{**self.status.model_dump(), **response["data"]})
            self.control = BaseControl(**{**self.control.model_dump(), **response["data"]})
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )
