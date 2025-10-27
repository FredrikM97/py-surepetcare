import pytest


@pytest.mark.devices("pet", "household")
@pytest.mark.cli_commands(
    ["pet", "--help"],
    ["pet", "list", "--household-id", "7777"],
    ["pet", "last-activity", "--household-id", "7777", "--pet-id", "123455"],
    ["pet", "assign-devices", "--household-id", "7777", "--pet-id", "123455"],
)
async def test_pet(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)
