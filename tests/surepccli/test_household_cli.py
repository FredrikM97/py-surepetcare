import pytest


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["household", "--help"],
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
