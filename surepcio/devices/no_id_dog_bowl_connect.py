from surepcio.enums import ProductId

from .device import BaseControl, BaseStatus, DeviceBase


class Control(BaseControl):
    pass


class Status(BaseStatus):
    pass


class NoIdDogBowlConnect(DeviceBase[Control, Status]):
    """Representation of a No ID Dog Bowl Connect device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.NO_ID_DOG_BOWL_CONNECT
