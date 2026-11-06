import logging
import math
from warnings import deprecated

from surepcio.command import Command
from surepcio.devices.entities import BowlState
from surepcio.entities.error_mixin import ImprovedErrorMixin
from surepcio.enums import (
    BowlPosition,
    BowlType,
    BowlTypeOptions,
    CloseDelay,
    FeederTrainingMode,
    FoodType,
    ProductId,
    Tare,
)

from .device import (
    BaseControl,
    BaseStatus,
    DeviceBase,
)

logger = logging.getLogger(__name__)


class BowlSetting(ImprovedErrorMixin):
    food_type: FoodType | None = None
    target: float | None = None


class Bowls(ImprovedErrorMixin):
    settings: list[BowlSetting | None] | None = None
    type: BowlType | None = None


class Lid(ImprovedErrorMixin):
    close_delay: CloseDelay | None = None


class Control(BaseControl):
    lid: Lid | None = None
    bowls: Bowls | None = None
    tare: Tare | None = None
    training_mode: FeederTrainingMode | None = None
    fast_polling: bool | None = None


class Status(BaseStatus):
    # pet_status: Optional[dict] = None
    bowl_status: list[BowlState] | None = None
    bowl_type_options: str | None = None
    fill_percentages: dict[str, float | None | dict[int, float | None]] | None = None
    tare_options: list[str] | None = None


class FeederConnect(DeviceBase[Control, Status]):
    controlCls = Control
    statusCls = Status

    @property
    def product(self) -> ProductId:
        return ProductId.FEEDER_CONNECT

    @property
    def photo(self) -> str:
        return "https://www.surepetcare.io/assets/assets/products/feeder.7ff330c9e368df01d256156b6fc797bb.png"

    def _after_refresh(self) -> None:
        bowls_type = self.control.bowls.type if self.control.bowls else None
        if bowls_type == BowlType.LARGE and self.status.bowl_status:
            bowl = self.status.bowl_status[0]
            bowl.position = BowlPosition.BOTH
            self.status.bowl_status = [bowl]

        self.status.bowl_type_options = self.get_bowl_type_option()
        self.status.fill_percentages = self.fill_percentages()
        self.status.tare_options = self.get_tare_options()

    @property
    def rssi(self) -> int | None:
        """Return the RSSI value."""
        return self.status.signal.device_rssi if self.status.signal else None

    @deprecated("In favor of set_bowl_type")
    def set_bowls(self, bowls: Bowls) -> Command:
        """Set bowls settings"""
        return self.set_control(bowls=bowls)

    def set_lid(self, closeDelay: CloseDelay) -> Command:
        """Set lid settings"""
        if isinstance(closeDelay, str):
            closeDelay = CloseDelay[closeDelay]
        return self.set_control(lid=Lid(close_delay=closeDelay))

    def set_tare(self, tare: Tare) -> Command:
        """Set tare settings"""
        return self.set_control(tare=tare)

    def set_target_weight(self, index: int, target: float) -> Command:
        """Update one bowl without discarding its food type or the other bowl."""
        if not isinstance(index, int) or isinstance(index, bool) or index not in (0, 1):
            raise ValueError(f"Invalid bowl index: {index!r}")
        if (
            isinstance(target, bool)
            or not isinstance(target, (int, float))
            or not math.isfinite(target)
        ):
            raise TypeError("Bowl target must be a finite number")
        if not 0 <= target <= 300 or int(target) != target:
            raise ValueError("Bowl target must be a whole number from 0 to 300")
        bowls = self.control.bowls
        settings = list(bowls.settings or ()) if bowls is not None else []
        while len(settings) <= index:
            settings.append(None)
        setting = settings[index]
        settings[index] = (
            setting.model_copy(update={"target": target})
            if setting is not None
            else BowlSetting(target=target)
        )
        return self.set_control(
            bowls=(
                bowls.model_copy(update={"settings": settings})
                if bowls is not None
                else Bowls(settings=settings)
            )
        )

    def set_training_mode(self, training_mode: FeederTrainingMode) -> Command:
        """Set training_mode settings"""
        return self.set_control(training_mode=training_mode)

    def set_bowl_type(self, option: BowlTypeOptions) -> object:
        """Set the bowl type/settings on the device using BowlTypeOptions enum."""
        if not isinstance(option, BowlTypeOptions):
            return None
        settings: list[BowlSetting | None] = [
            BowlSetting(food_type=ft.value, target=0) for ft in option.food_types
        ]
        return self.set_control(
            bowls=Bowls(type=option.bowl_type.value, settings=settings)
        )

    def get_bowl_type_option(self) -> str | None:
        """Return the BowlTypeOptions name matching the current device bowl settings."""
        bowls = self.control.bowls
        if not bowls or not bowls.type or not bowls.settings:
            return None
        bowl_type = bowls.type
        settings = (
            bowls.settings if isinstance(bowls.settings, list) else list(bowls.settings)
        )
        food_types = tuple(getattr(s, "food_type", None) for s in settings)
        for option in BowlTypeOptions:
            if option.bowl_type == bowl_type and tuple(option.food_types) == tuple(
                food_types
            ):
                return option.name
        return None

    def get_tare_options(self) -> list[str]:
        """Return the available tare options based on bowl type.

        Note: Returns hardcoded string names instead of enum values because
        RESET_LARGE and RESET_LEFT share the same enum value (1) in the API.
        """
        bowls = self.control.bowls
        if not bowls or not bowls.type:
            return []

        if bowls.type == BowlType.LARGE:
            return ["reset_large"]
        else:
            return ["reset_left", "reset_right", "reset_both"]

    def fill_percentages(self) -> dict[str, float | None | dict[int, float | None]]:
        """Return total and per-bowl fill percentages.

        Rules:
        - Negative calculated percentages are clamped to 0.
        - If weight is None, target is None, or target <= 0, that bowl returns None.
        - If no valid target values are available, total returns None.
        """
        bowl_status = getattr(self.status, "bowl_status", None)
        bowls = getattr(self.control, "bowls", None)
        bowl_settings = getattr(bowls, "settings", None)

        if not bowl_status or not bowl_settings:
            return {"total": None, "per_bowl": {}}

        total_weight = 0.0
        total_target = 0.0
        individual: dict[int, float | None] = {}

        for i, setting in enumerate(bowl_settings):
            if i >= len(bowl_status):
                break
            weight = bowl_status[i].current_weight
            target = getattr(setting, "target", None)

            if weight is None or target is None:
                individual[i] = None
                continue

            if target <= 0:
                individual[i] = None
                continue

            clamped_weight = max(weight, 0)
            percent = max((clamped_weight / target) * 100, 0)
            individual[i] = percent

            total_weight += clamped_weight
            total_target += target

        total: float | None = (
            max((total_weight / total_target) * 100, 0) if total_target > 0 else None
        )
        return {"total": total, "per_bowl": individual}
