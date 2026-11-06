import typer

from surepccli.helpers import household_option, pet_id_option, print_table
from surepccli.session import get_session_manager
from surepccli.typer import AsyncTyper
from surepcio.devices.pet import Pet
from surepcio.entities.pet import iter_pet_events, last_activity_reading
from surepcio.household import Household

pet = AsyncTyper(help="Pet commands", login_required=True)


async def _fetch_all_pets(household_id: str) -> list[Pet]:
    async with get_session_manager() as sm:
        # Dummy in order to populate the devices that is assigned
        household = Household({"id": household_id})
        await sm.client.api(household.get_devices())
        return await sm.client.api(household.get_pets())


async def _fetch_pets(
    household_id: str,
    pet_id: str | None = None,
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
async def last_activity(
    household_id: str = household_option(), pet_id: str = pet_id_option()
) -> None:
    """Show last activity for a pet"""
    pet: Pet = await _fetch_pet(household_id, pet_id)

    async with get_session_manager() as sm:
        events = await sm.client.api(Household({"id": household_id}).get_timeline())
        latest = next(
            (
                (matched_event.created_at, last_activity_reading(matched_event))
                for event in sorted(
                    (event for event in events if event.created_at is not None),
                    key=lambda event: (event.created_at, event.id),
                    reverse=True,
                )
                for _, matched_event in iter_pet_events(event, [pet])
            ),
            None,
        )
    if latest is None:
        typer.echo("No activity recorded yet.")
        return
    at, result = latest
    if result is None:
        raise ValueError("Timeline last activity must include a reading")
    typer.echo(f"Last activity for pet {pet.name} (ID: {pet.id}):")
    typer.echo(f"device_id: {result.attributes.get('device')}\ntime: {at!s}")


@pet.command()
async def assign_devices(
    household_id: str = household_option(), pet_id: str = pet_id_option()
) -> None:
    """Fetch assigned devices for a pet"""
    pet: Pet = await _fetch_pet(household_id, pet_id)

    async with get_session_manager() as sm:
        await sm.client.api(pet.refresh())

    typer.echo(f"Assigned devices for pet {pet.name} (ID: {pet.id}):")
    typer.echo(f"device_id: {[d.id for d in pet.status.devices.items]}")
    typer.echo(f"count: {pet.status.devices.count}")
