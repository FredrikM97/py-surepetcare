from typing import Optional

import typer

from .const import Envs
from surepccli.devices import device_subgroups
from surepccli.helpers import household_option
from surepccli.helpers import list_devices
from surepccli.helpers import product_id_option
from surepccli.session import clear_env
from surepccli.session import save_session
from surepccli.typer import AsyncTyper

devices = AsyncTyper(help="Devices commands", login_required=True)
for subgroup in device_subgroups():
    devices.add_typer(subgroup)


@devices.command("list", help="List devices")
async def list_device(
    product_id: Optional[str] = product_id_option(optional=True),
    household_id: str = household_option(),
):
    await list_devices(household_id=household_id, product_id=product_id)


@devices.command("connect", help="Select a device to work with")
async def connect(
    product_id: Optional[str] = product_id_option(optional=True),
    household_id: str = household_option(),
):
    items = await list_devices(household_id=household_id, product_id=product_id)
    if items:
        index = typer.prompt("Connect to device", type=int)
        if index < 0 or index >= len(items):
            typer.echo("Invalid device index.")
            raise typer.Exit(code=1)
        sel = items[index]
        save_session(
            {
                Envs.SELECTED_DEVICE: str(sel.id),
                Envs.SELECTED_PRODUCT_ID: str(getattr(sel.product_id, "value", sel.product_id)),
            }
        )


@devices.command("clear", help="Clear selected device")
async def clear_selected_device():
    clear_env(Envs.SELECTED_DEVICE)
    clear_env(Envs.SELECTED_PRODUCT_ID)


__all__ = ["devices"]
