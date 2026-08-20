from typing import Annotated, cast

import typer

from surepccli.devices.helper import EnumChoice
from surepccli.helpers import (
    device_id_option,
    fetch_device,
    household_option,
    state_option,
)
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.hub import Hub
from surepcio.enums import HubLedMode, HubPairMode

hub = AsyncTyper(name="hub", help="PetDoor device commands", login_required=True)


@hub.command()
async def led_mode(
    state: Annotated[
        HubLedMode | None,
        state_option(
            "Set LED mode (omit to show current).", click_type=EnumChoice(HubLedMode)
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """LED mode"""
    device: Hub = cast(Hub, await fetch_device(household_id, device_id))

    if state is None:
        led_mode = device.control.led_mode
        name = led_mode.name if led_mode is not None else None
        typer.echo(f"Device {device.id}\nled_mode: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_led_mode(state))

    typer.echo(f"Device {device_id} led_mode to {state.name}.")


@hub.command()
async def pairing_mode(
    state: Annotated[
        HubPairMode | None,
        state_option(
            "Set pairing mode (omit to show current).",
            click_type=EnumChoice(HubPairMode),
        ),
    ] = None,
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Pairing mode"""
    device: Hub = cast(Hub, await fetch_device(household_id, device_id))

    if state is None:
        pairing_mode = device.control.pairing_mode
        name = pairing_mode.name if pairing_mode is not None else None
        typer.echo(f"Device {device.id}\npairing_mode: {name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_pairing_mode(state))

    typer.echo(f"Device {device_id} pairing_mode to {state.name}.")
