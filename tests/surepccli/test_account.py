import pytest


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["account", "--help"],
    ["household", "--help"],
    ["household", "list"],
)
async def test_account(register_mocks, cli_capture, cli_run, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("auth")
async def test_login(register_mocks, cli_capture, cli_run):
    await cli_capture(["account", "login", "aemail", "--no-store"], input_text="0\n")
