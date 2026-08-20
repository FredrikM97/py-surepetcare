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
from surepcio.devices.dual_scan_connect import DualScanConnect
from surepcio.devices.entities import Curfew
from surepcio.enums import FlapLocking

dualscanconnect = AsyncTyper(
    name="dualscanconnect", help="Flap device commands", login_required=True
)


@dualscanconnect.command("curfew", help="Set flap curfew mode")
async def curfew(
    state: Annotated[
        object | None,
        state_option(
            "Set new curfew times (omit to show current).", click_type=CurfewParamType()
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Curfew times, using the household's timezone"""
    device: DualScanConnect = cast(
        DualScanConnect, await fetch_device(household_id, device_id)
    )

    if state is None:
        curfews = device.control.curfew or []
        typer.echo(
            f"Device {device.id}\ncurfew: {[curfew.model_dump() for curfew in curfews]}"
        )
        return

    if isinstance(state, Curfew):
        curfew_list: list[Curfew] = [state]
    elif isinstance(state, list) and all(isinstance(item, Curfew) for item in state):
        curfew_list = state
    else:
        raise typer.BadParameter(
            "Curfew must be a Curfew object or list of Curfew objects"
        )

    async with get_session_manager() as sm:
        await sm.client.api(device.set_curfew(curfew_list))

    typer.echo(f"Device {device_id} curfew set to {state}.")


@dualscanconnect.command("locking", help="Set flap locking mode")
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
    device: DualScanConnect = cast(
        DualScanConnect, await fetch_device(household_id, device_id)
    )

    if state is None:
        locking = device.control.locking
        name = locking.name if locking is not None else None
        typer.echo(f"Device {device.id}\nlocking: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_locking(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")
