import pytest

from surepccli import app
from tests.surepccli.conftest import list_all_typer_commands


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["household", "list"],
)
async def test_household(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["household", "connect"],
)
@pytest.mark.cli_inputs(
    "0",
)
async def test_household_connect(register_mocks, cli_capture, cli_command, cli_inputs):
    await cli_capture(cli_command, input_text=cli_inputs)


@pytest.mark.parametrize(
    "command_path",
    [cmd + ["--help"] for cmd in list_all_typer_commands(app, filters=["household"])],
)
async def test_household_cmd_help(command_path, cli_capture):
    await cli_capture(command_path)
