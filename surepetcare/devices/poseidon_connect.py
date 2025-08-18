from .device import BaseControl
from .device import BaseStatus
from .device import SurepyDevice
from surepetcare.command import Command
from surepetcare.const import API_ENDPOINT_PRODUCTION
from surepetcare.enums import ProductId


class Control(BaseControl):
    pass


class Status(BaseStatus):
    pass


class PoseidonConnect(SurepyDevice):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.status: Status = Status(**data)
        self.control: Control = Control(**data)

    def refresh(self):
        def parse(response):
            if not response:
                return self

            self.status = Status(**{**self.status.model_dump(), **response})
            self.control = Control(**{**self.control.model_dump(), **response})
            return self

        return Command(
            method="GET",
            endpoint=f"{API_ENDPOINT_PRODUCTION}/device/{self.id}",
            callback=parse,
        )

    @property
    def product(self) -> ProductId:
        return ProductId.POSEIDON_CONNECT
