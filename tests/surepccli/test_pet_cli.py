import pytest

from surepccli import app
from tests.surepccli.conftest import list_all_typer_commands


@pytest.mark.devices(
    "pet", "household", "pet_door", "poseidon_connect", "dual_scan_connect", "hub"
)
@pytest.mark.cli_commands(
    ["pet", "list", "--household-id", "7777"],
    ["pet", "last-activity", "--household-id", "7777", "--pet-id", "123455"],
    ["pet", "assign-devices", "--household-id", "7777", "--pet-id", "123455"],
)
async def test_pet(register_mocks, cli_capture, cli_command, add_api_json_response):
    add_api_json_response(
        "GET",
        "/api/timeline/household/7777",
        {
            "data": [
                {
                    "id": 2,
                    "type": 0,
                    "created_at": "2025-09-16T19:42:53+00:00",
                    "pets": [{"id": 123455}],
                    "movements": [{"device_id": 269654, "direction": 1}],
                },
                {
                    "id": 1,
                    "type": 0,
                    "created_at": "2025-09-15T19:42:53+00:00",
                    "pets": [{"id": 123455}],
                    "movements": [{"device_id": 123, "direction": 2}],
                },
            ]
        },
    )
    await cli_capture(cli_command)


@pytest.mark.devices(
    "pet", "household", "pet_door", "poseidon_connect", "dual_scan_connect", "hub"
)
@pytest.mark.parametrize(
    "events",
    [
        [],
        [
            {
                "id": 1,
                "type": 0,
                "created_at": "2025-09-16T19:42:53+00:00",
                "pets": [{"id": 999999}],
                "movements": [{"device_id": 269654, "direction": 1}],
            }
        ],
    ],
)
async def test_last_activity_does_not_fall_back_to_pet_reports(
    register_mocks, cli_run, add_api_json_response, events
):
    add_api_json_response("GET", "/api/timeline/household/7777", {"data": events})
    result = await cli_run(
        ["pet", "last-activity", "--household-id", "7777", "--pet-id", "123455"]
    )
    assert result.exit_code == 0, result.exception
    assert "No activity recorded yet." in result.output
    assert "269654" not in result.output


@pytest.mark.parametrize(
    "command_path",
    [cmd + ["--help"] for cmd in list_all_typer_commands(app, filters=["pet"])],
)
async def test_household_cmd_help(command_path, cli_capture):
    await cli_capture(command_path)
