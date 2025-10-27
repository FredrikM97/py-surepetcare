from typing import Optional

import typer

from surepccli.helpers import household_option
from surepccli.helpers import pet_id_option
from surepccli.helpers import print_table
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.pet import Pet
from surepcio.household import Household

pet = AsyncTyper(help="Pet commands", login_required=True)


async def _fetch_all_pets(household_id: str) -> list[Pet]:
    async with get_session_manager() as sm:
        return await sm.client.api(Household({"id": household_id}).get_pets())


async def _fetch_pets(
    household_id: str,
    pet_id: Optional[str] = None,
) -> list[Pet]:
    pets = await _fetch_all_pets(household_id)
    if pet_id:
        pets = [d for d in pets if str(d.id) == str(pet_id)]
    return pets


async def _fetch_pet(household_id: str, pet_id: str) -> Pet:
    for d in await _fetch_all_pets(household_id):
        if str(d.id) == str(pet_id):
            return d
    raise ValueError(f"Pet with ID {pet_id} not found in household {household_id}.")


@pet.command("list")
async def list_pets(household_id: str = household_option()) -> None:
    """List pets"""
    pets: list[Pet] = await _fetch_pets(household_id)
    if not pets:
        typer.echo("No pets found.")
        return
    rows = [[pet.id, pet.name] for pet in pets]
    print_table(rows, headers=["Tag", "Name"])


@pet.command()
async def last_activity(household_id: str = household_option(), pet_id: str = pet_id_option()) -> None:
    """Show last activity for a pet"""
    pet: Pet = await _fetch_pet(household_id, pet_id)

    async with get_session_manager() as sm:
        pet = await sm.client.api(pet.refresh())

    result = pet.last_activity()
    if result is None:
        typer.echo("No activity recorded yet.")
        return
    time, device_id = result
    typer.echo(f"Last activity for pet {pet.name} (ID: {pet.id}):")
    typer.echo(f"device_id: {device_id}\ntime: {str(time)}")


@pet.command()
async def assign_devices(household_id: str = household_option(), pet_id: str = pet_id_option()) -> None:
    """Fetch assigned devices for a pet"""
    pet: Pet = await _fetch_pet(household_id, pet_id)

    async with get_session_manager() as sm:
        pet = await sm.client.api(pet.refresh())

    typer.echo(f"Assigned devices for pet {pet.name} (ID: {pet.id}):")
    typer.echo(f"device_id: {[d.id for d in pet.status.devices or []]}")
