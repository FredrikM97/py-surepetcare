from typing import cast
from typing import Optional

import typer

from surepccli.devices.helper import CurfewParamType
from surepccli.devices.helper import EnumChoice
from surepccli.helpers import device_id_option
from surepccli.helpers import fetch_device
from surepccli.helpers import household_option
from surepccli.helpers import state_option
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.entities import Curfew
from surepcio.devices.pet_door import PetDoor
from surepcio.enums import FlapLocking


petdoor = AsyncTyper(name="petdoor", help="PetDoor device commands", login_required=True)


@petdoor.command("curfew", help="Set locking mode")
async def curfew(
    state: Optional[Curfew] = state_option(
        "Set new curfew times (omit to show current).", click_type=CurfewParamType()
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Curfew times, using the household's timezone"""
    device: PetDoor = cast(PetDoor, await fetch_device(household_id, device_id))

    if state is None:
        curfew = getattr(device.control, "curfew")
        typer.echo(f"Device {device.id}\ncurfew: {curfew.model_dump()}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_curfew(state))

    typer.echo(f"Device {device_id} curfew set to {state}.")


@petdoor.command("locking", help="Set flap locking mode")
async def locking(
    state: FlapLocking = state_option(
        "Set new locking mode (omit to show current).", click_type=EnumChoice(FlapLocking)
    ),
    device_id: str = device_id_option(),
    household_id: str = household_option(),
):
    """Locking mode"""
    device: PetDoor = cast(PetDoor, await fetch_device(household_id, device_id))

    if state is None:
        locking = getattr(device.control, "locking")
        typer.echo(f"Device {device.id}\nLocking: {locking.name}")
        return
    async with get_session_manager() as sm:
        await sm.client.api(device.set_locking(state))

    typer.echo(f"Device {device_id} lock set to {state.name}.")
