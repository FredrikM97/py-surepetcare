from typing import Annotated, cast

import typer

from surepccli.devices.helper import EnumChoice
from surepccli.helpers import (
    device_id_option,
    fetch_device,
    household_option,
    print_table,
    state_option,
)
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.enums import BowlTypeOptions, CloseDelay, FeederTrainingMode, Tare

feederconnect = AsyncTyper(
    name="feederconnect", help="Feeder device commands", login_required=True
)


@feederconnect.command(login_required=True)
async def fill_percentages(
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(
        FeederConnect, await fetch_device(household_id, device_id)
    )

    if not device:
        return
    result = device.fill_percentages()
    total_value = result.get("total")
    total = total_value if isinstance(total_value, (int, float)) else None

    bowls_value = result.get("per_bowl", {})
    bowls = bowls_value if isinstance(bowls_value, dict) else {}

    rows = [
        [f"Bowl {b}", f"{round(p, 2) if p is not None else 'N/A'}"]
        for b, p in (bowls or {}).items()
    ]
    if total is not None:
        rows.append(["Total", f"{int(total)}"])
    print_table(rows, headers=["Type", "Percentage"])


@feederconnect.command(login_required=True)
async def lid_delay(
    state: Annotated[
        CloseDelay | None,
        state_option(
            "Set new lid close delay (omit to show current).",
            click_type=EnumChoice(CloseDelay),
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(
        FeederConnect, await fetch_device(household_id, device_id)
    )
    if state is None:
        delay = device.control.lid.close_delay if device.control.lid else None
        name = delay.name if delay is not None else None
        typer.echo(f"Device {device.id}\nlid_delay: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_lid(state))
    typer.echo(f"Device {device.id} lid delay set to {state.name}.")


@feederconnect.command(login_required=True)
async def training_mode(
    state: Annotated[
        FeederTrainingMode | None,
        state_option(
            "Set new training mode (omit to show current).",
            click_type=EnumChoice(FeederTrainingMode),
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(
        FeederConnect, await fetch_device(household_id, device_id)
    )

    if state is None:
        training_mode = device.control.training_mode
        name = training_mode.name if training_mode is not None else None
        typer.echo(f"Device {device.id}\ntraining_mode: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_training_mode(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")


@feederconnect.command(login_required=True)
async def tare(
    state: Annotated[
        Tare | None,
        state_option(
            "Set tare settings (omit to show current).", click_type=EnumChoice(Tare)
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(
        FeederConnect, await fetch_device(household_id, device_id)
    )

    if state is None:
        tare = device.control.tare
        tare = getattr(tare, "name", None)
        typer.echo(f"Device {device.id}\ntare: {tare}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_tare(state))

    typer.echo(f"Device {device_id} tare set to {state.name}.")


@feederconnect.command(login_required=True)
async def bowl_type(
    state: Annotated[
        BowlTypeOptions | None,
        state_option(
            "Set bowl type/settings (omit to show current).",
            click_type=EnumChoice(BowlTypeOptions),
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(
        FeederConnect, await fetch_device(household_id, device_id)
    )

    if state is None:
        bowls = device.control.bowls
        dump = bowls.model_dump() if bowls is not None else None
        typer.echo(f"Device {device.id}\nbowls: {dump}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_bowl_type(state))

    typer.echo(f"Device {device_id} bowls set to {state.name}.")


@feederconnect.command(login_required=True)
async def bowl_type_options(
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    device: FeederConnect = cast(
        FeederConnect, await fetch_device(household_id, device_id)
    )
    typer.echo(
        f"Device {device_id}\nAvailable Options:\n{device.get_bowl_type_option()}"
    )
