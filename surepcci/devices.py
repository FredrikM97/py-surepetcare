from typing import Optional

import click

from surepcci.context import async_command
from surepcci.context import Context
from surepcci.context import print_table
from surepcio.household import Household


@click.group()
def devices():
    """Devices commands"""
    pass


@click.group()
def dualscanconnect():
    """Flap device commands"""
    pass


@click.group()
def feederconnect():
    """Feeder device commands"""
    pass


@devices.command("list")
@click.pass_obj
@async_command
@click.option("--product-id", type=str, default=None, help="Filter by ProductId")
async def list_devices(ctx: Context, product_id: Optional[str] = None):
    """List all devices"""
    household: Household = await ctx.client.api(Household.get_household(ctx.household_id))
    devices = await ctx.client.api(household.get_devices())

    if not devices:
        click.echo("No devices found.")
        return

    if product_id:
        devices = [
            d
            for d in devices
            if str(d.product_id) == product_id or getattr(d.product_id, "name", "") == product_id
        ]

    rows = [[device.id, device.name, device.product_id] for device in devices]
    print_table(rows, headers=["ID", "Name", "ProductId"])


@feederconnect.command()
@click.argument("device_id")
def get_lid(device_id):
    """Get feeder lid state"""
    click.echo(f"lid_state: closed (device {device_id})")


@feederconnect.command()
@click.argument("device_id")
@click.argument("state")
def set_lid(device_id, state):
    """Set feeder lid state"""
    click.echo(f"Feeder {device_id} lid {state}ed.")


@dualscanconnect.command()
@click.argument("device_id")
@click.argument("state")
def set_lock(device_id, state):
    """Set flap lock state"""
    click.echo(f"Flap {device_id} lock set to {state}.")


@dualscanconnect.command()
@click.argument("device_id")
def get_lock(device_id):
    """Get flap lock state"""
    click.echo(f"Flap {device_id} lock state: unlocked.")
