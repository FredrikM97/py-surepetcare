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
from surepcio.devices.dual_scan_pet_door import DualScanPetDoor
from surepcio.devices.entities import Curfew
from surepcio.enums import FlapLocking

dualscanpetdoor = AsyncTyper(
    name="dualscanpetdoor", help="DualScanPetDoor device commands", login_required=True
)


@dualscanpetdoor.command("curfew", help="Set flap locking mode")
async def curfew(
    state: Annotated[
        list[Curfew] | None,
        state_option(
            "Set new curfew times (omit to show current).", click_type=CurfewParamType()
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Curfew times, using the household's timezone"""
    device: DualScanPetDoor = cast(
        DualScanPetDoor, await fetch_device(household_id, device_id)
    )

    if state is None:
        curfews = device.control.curfew or []
        typer.echo(
            f"Device {device.id}\ncurfew: {[curfew.model_dump() for curfew in curfews]}"
        )
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_curfew(state))

    typer.echo(f"Device {device_id} curfew set to {state}.")


@dualscanpetdoor.command("locking", help="Set flap locking mode")
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
    device: DualScanPetDoor = cast(
        DualScanPetDoor, await fetch_device(household_id, device_id)
    )

    if state is None:
        locking = device.control.locking
        name = locking.name if locking is not None else None
        typer.echo(f"Device {device.id}\nlocking: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_locking(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")
