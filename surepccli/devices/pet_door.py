from typing import Annotated, cast

import typer

from surepccli.devices.helper import CurfewParamType, EnumChoice
from surepccli.helpers import (
    device_id_option,
    fetch_device,
    household_option,
    state_option,
)
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.entities import Curfew
from surepcio.devices.pet_door import PetDoor
from surepcio.enums import FlapLocking

petdoor = AsyncTyper(
    name="petdoor", help="PetDoor device commands", login_required=True
)


@petdoor.command("curfew", help="Set locking mode")
async def curfew(
    state: Annotated[
        Curfew | None,
        state_option(
            "Set new curfew times (omit to show current).", click_type=CurfewParamType()
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Curfew times, using the household's timezone"""
    device: PetDoor = cast(PetDoor, await fetch_device(household_id, device_id))

    if state is None:
        curfew = device.control.curfew
        dump = curfew.model_dump() if curfew is not None else None
        typer.echo(f"Device {device.id}\ncurfew: {dump}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_curfew(state))

    typer.echo(f"Device {device_id} curfew set to {state}.")


@petdoor.command("locking", help="Set flap locking mode")
async def locking(
    state: Annotated[
        FlapLocking | None,
        state_option(
            "Set new locking mode (omit to show current).",
            click_type=EnumChoice(FlapLocking),
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Locking mode"""
    device: PetDoor = cast(PetDoor, await fetch_device(household_id, device_id))

    if state is None:
        locking = device.control.locking
        name = locking.name if locking is not None else None
        typer.echo(f"Device {device.id}\nLocking: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_locking(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")
