import click

from .account import household
from .context import cli
from .devices import devices
from .devices import dualscanconnect
from .devices import feederconnect
from .pet import pet


def register_device_commands(cli: click.Group) -> None:
    """Register all device command groups to the main CLI."""
    cli.add_command(household)
    cli.add_command(devices)
    cli.add_command(pet)

    # Register subgroups to the parent group
    devices.add_command(dualscanconnect)
    devices.add_command(feederconnect)


def main():
    register_device_commands(cli)
    cli()
