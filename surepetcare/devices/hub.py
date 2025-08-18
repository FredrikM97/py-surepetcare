from .device import BaseControl
from .device import BaseStatus
from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId


class Hub(SurepyDevice):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.status: BaseStatus = BaseStatus(**data)
        self.control: BaseControl = BaseControl(**data)

    @property
    def product(self) -> ProductId:
        return ProductId.HUB

    @property
    def photo(self) -> str:
        return (
            "https://www.surepetcare.io/assets/assets/products/hub/hub.6475b3a385180ab8fb96731c4bfd1eda.png"
        )

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
