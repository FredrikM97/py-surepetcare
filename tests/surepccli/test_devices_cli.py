import pytest


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["devices", "--help"],
    ["devices", "list", "--help"],
    ["devices", "list", "--household-id", "7777"],
    ["devices", "clear"],
)
async def test_devices(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["devices", "connect", "--household-id", "7777"],
)
@pytest.mark.cli_inputs("0\n")
async def test_devices_connect(register_mocks, cli_capture, cli_command, cli_inputs):
    await cli_capture(cli_command, cli_inputs)


@pytest.mark.devices("feeder_connect", "household")
@pytest.mark.cli_commands(
    ["devices", "feederconnect", "fill-percentages", "--household-id", "7777", "--device-id", "1187564"],
    ["devices", "feederconnect", "lid_delay", "--household-id", "7777", "--device-id", "1187564"],
    ["devices", "feederconnect", "training-mode", "--household-id", "7777", "--device-id", "1187564"],
    ["devices", "feederconnect", "bowl-type", "--household-id", "7777", "--device-id", "1187564"],
    ["devices", "feederconnect", "tare", "--household-id", "7777", "--device-id", "1187564"],
    ["devices", "feederconnect", "bowl-type-options", "--household-id", "7777", "--device-id", "1187564"],
)
async def test_feederconnect(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("dual_scan_connect", "household")
@pytest.mark.cli_commands(
    ["devices", "dualscanconnect", "--help"],
    ["devices", "dualscanconnect", "curfew", "--household-id", "7777", "--device-id", "1334025"],
    ["devices", "dualscanconnect", "locking", "--household-id", "7777", "--device-id", "1334025"],
)
async def test_dualscanconnect(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("pet_door", "household")
@pytest.mark.cli_commands(
    ["devices", "petdoor", "--help"],
    ["devices", "petdoor", "curfew", "--household-id", "7777", "--device-id", "727608"],
    ["devices", "petdoor", "locking", "--household-id", "7777", "--device-id", "727608"],
)
async def test_petdoor(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)


@pytest.mark.devices("hub", "household")
@pytest.mark.cli_commands(
    ["devices", "hub", "--help"],
    ["devices", "hub", "led-mode", "--household-id", "7777", "--device-id", "295972"],
    ["devices", "hub", "pairing-mode", "--household-id", "7777", "--device-id", "295972"],
)
async def test_hub(register_mocks, cli_capture, cli_command):
    await cli_capture(cli_command)
