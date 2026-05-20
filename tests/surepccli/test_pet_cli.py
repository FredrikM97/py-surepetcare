import pytest

from surepccli import app
from tests.surepccli.conftest import list_all_typer_commands


@pytest.mark.devices("pet", "household", "pet_door", "poseidon_connect", "dual_scan_connect", "hub")
@pytest.mark.cli_commands(
    ["pet", "list", "--household-id", "7777"],
    ["pet", "last-activity", "--household-id", "7777", "--pet-id", "123455"],
    ["pet", "assign-devices", "--household-id", "7777", "--pet-id", "123455"],
)
async def test_pet(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.parametrize(
    "command_path", [cmd + ["--help"] for cmd in list_all_typer_commands(app, filters=["pet"])]
)
async def test_household_cmd_help(command_path, cli_capture):
    await cli_capture(command_path)
