import pytest

from surepccli import app
from tests.surepccli.conftest import list_all_typer_commands


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["account", "info"], ["account", "logout"], ["account", "token"]
)
async def test_account(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("auth")
@pytest.mark.cli_commands(
    ["account", "login", "aemail", "--no-store"],
    ["account", "login", "aemail"],
)
@pytest.mark.cli_inputs(
    "password123",
    "password123",
)
async def test_login(register_mocks, cli_capture, cli_command, cli_inputs):
    await cli_capture(cli_command, cli_inputs)


@pytest.mark.parametrize(
    "command_path",
    [cmd + ["--help"] for cmd in list_all_typer_commands(app, filters=["account"])],
)
async def test_household_cmd_help(command_path, cli_capture):
    await cli_capture(command_path)
