import enum
import json

import click

from surepcio.devices.entities import Curfew


class CurfewParamType(click.ParamType):
    name = "curfew"

    def convert(self, value, param, ctx) -> Curfew | list[Curfew] | None:
        raw = (value or "").strip()
        try:
            # Accept JSON object or list of objects
            data = json.loads(raw)
            if isinstance(data, dict):
                return Curfew(**data)
            elif isinstance(data, list):
                return [Curfew(**item) for item in data]
            else:
                self.fail("Curfew must be a JSON object or list of objects", param, ctx)
        except Exception as e:
            self.fail(f"Invalid curfew '{value}': {e}", param, ctx)
        return None


class EnumChoice(click.ParamType):
    """A Click param type that shows enum choices and returns the enum instance."""

    def __init__(self, enum_cls: type[enum.Enum]) -> None:
        if not issubclass(enum_cls, enum.Enum):
            raise TypeError(f"{enum_cls} is not an Enum type")
        self.enum_cls = enum_cls
        self.name = enum_cls.__name__

    def get_metavar(self, param: click.Parameter, ctx: click.Context) -> str | None:
        return f"[{'|'.join(self.enum_cls._member_names_)}]"

    def get_missing_message(
        self, param: click.Parameter, ctx: click.Context | None
    ) -> str | None:
        return f"Choose from: {', '.join(self.enum_cls._member_names_)}"

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> enum.Enum:
        if isinstance(value, self.enum_cls):
            return value
        try:
            return self.enum_cls[value]
        except KeyError:
            # Try by value
            for member in self.enum_cls:
                if member.value == value:
                    return member
            self.fail(
                f"{value!r} is not a valid {self.enum_cls.__name__}. "
                f"Choose from: {', '.join(self.enum_cls._member_names_)}",
                param,
                ctx,
            )
