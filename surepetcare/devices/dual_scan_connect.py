from .device import BaseControl
from .device import BaseStatus
from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId


class DualScanConnect(SurepyDevice):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.status: BaseStatus = BaseStatus(**data)
        self.control: BaseControl = BaseControl(**data)

    @property
    def product(self) -> ProductId:
        return ProductId.DUAL_SCAN_CONNECT

    def refresh(self):
        def parse(response):
            if not response:
                return self

            self.status = BaseStatus(**{**self.status.model_dump(), **response})
            self.control = BaseControl(**{**self.control.model_dump(), **response})
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )
