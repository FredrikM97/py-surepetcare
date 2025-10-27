import os

import typer

from .const import Envs
from .helpers import print_table
from .typer import AsyncTyper
from surepccli.session import clear_session
from surepccli.session import get_session_manager
from surepccli.session import save_session
from surepcio.household import Household


account = AsyncTyper(help="Account commands")
household = AsyncTyper(help="Household commands")


@account.command()
async def login(
    email: str,
    password: str = typer.Option(
        None, "--password", prompt=True, hide_input=True, help="Account password (prompted, hidden)."
    ),
    store: bool = typer.Option(True, "--no-store", help="Do not store session in environment."),
):
    """Login with email and password."""
    async with get_session_manager() as sm:
        await sm.client.login(email=email, password=password)
    if store:
        save_session({Envs.TOKEN: sm.client.token, Envs.CLIENT_ID: str(sm.client.device_id)})

    typer.echo(f"Logged in as {email}.")


@account.command()
async def info():
    """Show account info."""
    info_data = []
    for key in Envs:
        # Skip showing the token for bloating the output
        if key == Envs.TOKEN:
            continue
        value = os.getenv(key)
        status = value if value else "not set"
        info_data.append((key, status))
    typer.echo("Account info:")
    print_table(info_data, headers=["Key", "Value"])


@account.command()
async def token():
    """Show account token."""

    value = os.getenv(Envs.TOKEN)
    typer.echo(value if value else "not set")


@account.command()
async def logout():
    """Logout and clear session."""
    clear_session()
    typer.echo("You have been logged out.")


@household.command("list", help="List households", login_required=True)
async def list_household() -> None:
    """List households"""
    async with get_session_manager() as sm:
        households = await sm.client.api(Household.get_households())

    if not households:
        typer.echo("No households found.")
        return
    typer.echo("Households:")
    data = [(h.id, h.data["name"]) for idx, h in enumerate(households)]

    print_table(data, headers=["ID", "Name"])


@household.command(help="Connect to a household", login_required=True)
async def connect() -> None:
    """List households"""
    async with get_session_manager() as sm:
        households = await sm.client.api(Household.get_households())

    if not households:
        typer.echo("No households found.")
        return
    typer.echo("Households:")
    data = [(idx, h.id, h.data["name"]) for idx, h in enumerate(households)]

    print_table(data, headers=["select", "ID", "Name"])
    index = typer.prompt("Select household", type=int)
    save_session({Envs.HOUSEHOLD_ID: str(data[index][1])})
    typer.echo(f"Connected to {data[index][2]}")
