import pytest


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["account", "--help"], ["account", "info"], ["account", "logout"], ["account", "token"]
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
