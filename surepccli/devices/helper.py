import json

import click

from surepcio.devices.entities import Curfew


class CurfewParamType(click.ParamType):
    name = "curfew"

    def convert(self, value, param, ctx):
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
