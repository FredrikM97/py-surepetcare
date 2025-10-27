from typing import cast

import typer

from surepccli.devices.helper import CurfewParamType
from surepccli.devices.helper import EnumChoice
from surepccli.helpers import device_id_option
from surepccli.helpers import fetch_device
from surepccli.helpers import household_option
from surepccli.helpers import state_option
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.dual_scan_connect import DualScanConnect
from surepcio.devices.entities import Curfew
from surepcio.enums import FlapLocking

dualscanconnect = AsyncTyper(name="dualscanconnect", help="Flap device commands", login_required=True)


@dualscanconnect.command("curfew", help="Set flap curfew mode")
async def curfew(
    state: Curfew = state_option(  # typer works poorly with List[Curfew] but Curfew works.. fix later
        "Set new curfew times (omit to show current).", click_type=CurfewParamType()
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Curfew times, using the household's timezone"""
    device: DualScanConnect = cast(DualScanConnect, await fetch_device(household_id, device_id))

    if state is None:
        curfews = getattr(device.control, "curfew")
        typer.echo(f"Device {device.id}\ncurfew: {[curfew.model_dump() for curfew in curfews]}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_curfew(state))

    typer.echo(f"Device {device_id} curfew set to {state}.")


@dualscanconnect.command("locking", help="Set flap locking mode")
async def locking(
    state: FlapLocking = state_option(
        "Set new locking mode (omit to show current).", click_type=EnumChoice(FlapLocking)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Locking mode"""
    device: DualScanConnect = cast(DualScanConnect, await fetch_device(household_id, device_id))

    if state is None:
        locking = getattr(device.control, "locking")
        typer.echo(f"Device {device.id}\nlocking: {locking.name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_locking(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")
