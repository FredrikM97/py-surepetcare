import click

from surepcci.context import async_command
from surepcci.context import cli
from surepcci.context import Context
from surepcio.client import SurePetcareClient
from surepcio.household import Household


@click.group()
def household():
    """Household commands"""
    pass


@cli.command()
@click.pass_obj
@click.argument("email")
@click.argument("password")
@async_command
async def login(ctx: Context, email: str, password: str) -> None:
    """Login with email and password."""
    ctx.client = SurePetcareClient()
    await ctx.client.login(email=email, password=password)
    ctx.save_session(token=ctx.client._token, device_id=ctx.client._device_id)
    click.echo(f"Logged in as {email}")


@household.command()
@click.pass_obj
@click.argument("household_id")
def connect(ctx: Context, household_id):
    """Connect to a household"""
    ctx.save_session(household_id=household_id)
    click.echo(f"Connected to hub-{household_id} (stored in session context)")


@household.command("list")
@click.pass_obj
@async_command
async def list_households(ctx: Context):
    """List households"""
    households: list[Household] = await ctx.client.api(Household.get_households())
    if not households:
        click.echo("No households found.")
        return
    click.echo("Households:")
    for h in households:
        click.echo(f"{h.id}: {h.data.get('name', '(no name)')}")
