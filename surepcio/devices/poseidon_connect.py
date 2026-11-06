import logging

from surepcio.devices.entities import BowlState
from surepcio.enums import ProductId

from .device import BaseControl, BaseStatus, DeviceBase

logger = logging.getLogger(__name__)


class Control(BaseControl):
    learn_mode: bool | None = None
    fast_polling: bool | None = None


class Status(BaseStatus):
    bowl_status: list[BowlState] | None = None


class PoseidonConnect(DeviceBase[Control, Status]):
    """Representation of a Poseidon Connect device."""

    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.POSEIDON_CONNECT
