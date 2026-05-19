import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion
from surepcio import SurePetcareClient
from surepcio.command import Command
from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.devices.feeder_connect import FeederConnect
from surepcio.security.exceptions import ApiError
from tests.conftest import add_api_json_response
from tests.conftest import object_snapshot


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [204, 304])
async def test_get_none_status(aresponses: aresponses.ResponsesMockServer, status):
    aresponses.add(
        "example.com",
        "/endpoint",
        "GET",
        aresponses.Response(text="", status=status, headers={"Content-Type": "application/json"}),
    )
    async with SurePetcareClient() as client:
        result = await client.get("https://example.com/endpoint", params=None)
        result = result.data
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,error_text",
    [
        (400, "bad request"),
        (401, "unauthorized"),
        (403, "forbidden"),
        (404, "not found"),
        (405, "method not allowed"),
        (418, "teapot"),
        (500, "server error"),
    ],
)
async def test_api_error_for_various_statuses(
    aresponses: aresponses.ResponsesMockServer,
    snapshot: SnapshotAssertion,
    status: int,
    error_text: str,
):
    endpoint = "https://example.com/endpoint"
    add_api_json_response(aresponses, "GET", endpoint, {"error": error_text}, status=status)

    async with SurePetcareClient() as client:
        with pytest.raises(ApiError) as exc_info:
            await client.get(endpoint, params=None)

    err = exc_info.value
    object_snapshot(err, snapshot)


@pytest.mark.asyncio
async def test_async_put_with_pending_and_polling(aresponses: aresponses.ResponsesMockServer):
    """Test async PUT operation with pending results that completes via polling."""
    device_endpoint = f"{API_ENDPOINT_PRODUCTION}/device/123"

    # Mock PUT response with pending status (status_id=5)
    add_api_json_response(
        aresponses,
        "PUT",
        f"{device_endpoint}/control",
        {"data": {"id": 123, "control": {}}, "pending": [{"request_id": "abc", "status_id": 5}]},
    )

    # Mock polling response (status changed to 0=completed)
    add_api_json_response(
        aresponses,
        "GET",
        f"{API_ENDPOINT_PRODUCTION}/household/7777/device/control/status",
        {"results": [{"request_id": "abc", "status_id": 0}]},
    )

    # Mock device refresh
    add_api_json_response(
        aresponses,
        "GET",
        device_endpoint,
        {"data": {"id": 123, "control": {"bowls": None}, "status": {}, "household_id": 7777}},
    )

    async with SurePetcareClient() as client:
        device = FeederConnect({"id": 123, "household_id": 7777})

        cmd = Command(
            method="PUT",
            endpoint=f"{device_endpoint}/control",
            device=device,
        )
        result = await client.api(cmd)
        assert result is not None


@pytest.mark.asyncio
async def test_non_async_put_updates_device(aresponses: aresponses.ResponsesMockServer):
    """Test non-async PUT updates device control directly."""
    device_endpoint = f"{API_ENDPOINT_PRODUCTION}/device/456"

    # Mock PUT response with completed status (status_id=0)
    add_api_json_response(
        aresponses,
        "PUT",
        f"{device_endpoint}/control",
        {
            "data": {
                "id": 456,
                "control": {"bowls": {"type": 1}},
                "status": {"online": True},
            },
            "pending": [],
        },
    )

    # Mock refresh endpoint
    add_api_json_response(
        aresponses,
        "GET",
        device_endpoint,
        {"data": {"id": 456, "control": {"bowls": {"type": 1}}, "status": {"online": True}}},
    )

    async with SurePetcareClient() as client:
        device = FeederConnect({"id": 456, "household_id": 7777})

        cmd = Command(
            method="PUT",
            endpoint=f"{device_endpoint}/control",
            device=device,
        )
        result = await client.api(cmd)
        assert result is not None


@pytest.mark.asyncio
async def test_async_post_with_device_refresh(aresponses: aresponses.ResponsesMockServer):
    """Test async POST operation with pending results."""
    device_endpoint = f"{API_ENDPOINT_PRODUCTION}/device/789"

    # Mock POST response with pending status
    add_api_json_response(
        aresponses,
        "POST",
        f"{device_endpoint}/control",
        {"data": {}, "pending": [{"request_id": "post1", "status_id": 5}]},
    )

    # Mock polling response (completed)
    add_api_json_response(
        aresponses,
        "GET",
        f"{API_ENDPOINT_PRODUCTION}/household/8888/device/control/status",
        {"results": [{"request_id": "post1", "status_id": 0}]},
    )

    # Mock device refresh
    add_api_json_response(
        aresponses,
        "GET",
        device_endpoint,
        {"data": {"id": 789, "control": {}, "status": {}, "household_id": 8888}},
    )

    async with SurePetcareClient() as client:
        device = FeederConnect({"id": 789, "household_id": 8888})

        cmd = Command(
            method="POST",
            endpoint=f"{device_endpoint}/control",
            device=device,
        )
        result = await client.api(cmd)
        assert result is not None
