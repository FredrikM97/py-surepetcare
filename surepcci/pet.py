import click

from surepcci.context import async_command
from surepcci.context import Context
from surepcci.context import print_table
from surepcio.devices.pet import Pet
from surepcio.household import Household


@click.group()
def pet():
    """Pet commands"""
    pass


@pet.command("list")
@click.pass_obj
@async_command
async def list_pets(ctx: Context):
    """List pets"""
    household: Household = await ctx.client.api(Household.get_household(ctx.household_id))
    pets: list[Pet] = await ctx.client.api(household.get_pets())

    if not pets:
        click.echo("No pets found.")
        return

    rows = [[pet.id, pet.name] for pet in pets]
    print_table(rows, headers=["Tag", "Name"])
