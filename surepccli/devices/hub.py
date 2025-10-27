from typing import cast

import typer

from surepccli.devices.helper import EnumChoice
from surepccli.helpers import device_id_option
from surepccli.helpers import fetch_device
from surepccli.helpers import household_option
from surepccli.helpers import state_option
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.hub import Hub
from surepcio.enums import HubLedMode
from surepcio.enums import HubPairMode


hub = AsyncTyper(name="hub", help="PetDoor device commands", login_required=True)


@hub.command()
async def led_mode(
    state: HubLedMode = state_option(
        "Set LED mode (omit to show current).", click_type=EnumChoice(HubLedMode)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """LED mode"""
    device: Hub = cast(Hub, await fetch_device(household_id, device_id))

    if state is None:
        led_mode = getattr(device.control, "led_mode")
        typer.echo(f"Device {device.id}\nled_mode: {led_mode.name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_led_mode(state))

    typer.echo(f"Device {device_id} led_mode to {state.name}.")


@hub.command()
async def pairing_mode(
    state: HubPairMode = state_option(
        "Set pairing mode (omit to show current).", click_type=EnumChoice(HubPairMode)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Pairing mode"""
    device: Hub = cast(Hub, await fetch_device(household_id, device_id))

    if state is None:
        pairing_mode = getattr(device.control, "pairing_mode")
        typer.echo(f"Device {device.id}\npairing_mode: {pairing_mode.name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_pairing_mode(state))

    typer.echo(f"Device {device_id} pairing_mode to {state.name}.")
