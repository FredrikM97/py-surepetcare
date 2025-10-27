from typing import cast

import typer

from surepccli.devices.helper import EnumChoice
from surepccli.helpers import device_id_option
from surepccli.helpers import fetch_device
from surepccli.helpers import household_option
from surepccli.helpers import print_table
from surepccli.helpers import state_option
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.enums import BowlTypeOptions
from surepcio.enums import CloseDelay
from surepcio.enums import FeederTrainingMode
from surepcio.enums import Tare

feederconnect = AsyncTyper(name="feederconnect", help="Feeder device commands", login_required=True)


@feederconnect.command(login_required=True)
async def fill_percentages(
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(FeederConnect, await fetch_device(household_id, device_id))

    if not device:
        return
    result = device.fill_percentages()
    if isinstance(result, tuple):
        total, bowls = result
    else:
        total, bowls = None, {}
    rows = [[f"Bowl {b}", f"{round(p, 2) if p is not None else 'N/A'}"] for b, p in (bowls or {}).items()]
    if total is not None:
        rows.append(["Total", f"{int(total)}"])
    print_table(rows, headers=["Type", "Percentage"])


@feederconnect.command(login_required=True)
async def lid_delay(
    state: CloseDelay = state_option(
        "Set new lid close delay (omit to show current).", click_type=EnumChoice(CloseDelay)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(FeederConnect, await fetch_device(household_id, device_id))
    if state is None:
        delay = getattr(device.control.lid, "close_delay")
        typer.echo(f"Device {device.id}\nlid_delay: {delay.name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_lid(state))
    typer.echo(f"Device {device.id} lid delay set to {state.name}.")


@feederconnect.command(login_required=True)
async def training_mode(
    state: FeederTrainingMode = state_option(
        "Set new training mode (omit to show current).", click_type=EnumChoice(FeederTrainingMode)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(FeederConnect, await fetch_device(household_id, device_id))

    if state is None:
        training_mode = getattr(device.control, "training_mode")
        typer.echo(f"Device {device.id}\ntraining_mode: {training_mode.name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_training_mode(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")


@feederconnect.command(login_required=True)
async def tare(
    state: Tare = state_option("Set tare settings (omit to show current).", click_type=EnumChoice(Tare)),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(FeederConnect, await fetch_device(household_id, device_id))

    if state is None:
        tare = getattr(device.control, "tare")
        tare = getattr(tare, "name", None)
        typer.echo(f"Device {device.id}\ntare: {tare}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_tare(state))

    typer.echo(f"Device {device_id} tare set to {state.name}.")


@feederconnect.command(login_required=True)
async def bowl_type(
    state: BowlTypeOptions = state_option(
        "Set bowl type/settings (omit to show current).", click_type=EnumChoice(BowlTypeOptions)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(FeederConnect, await fetch_device(household_id, device_id))

    if state is None:
        bowls = getattr(device.control, "bowls")
        typer.echo(f"Device {device.id}\nbowls: {bowls.model_dump()}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_bowl_type(state))

    typer.echo(f"Device {device_id} bowls set to {state.name}.")


@feederconnect.command(login_required=True)
async def bowl_type_options(
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(FeederConnect, await fetch_device(household_id, device_id))
    typer.echo(f"Device {device_id}\nAvailable Options:\n{device.get_bowl_type_option()}")
