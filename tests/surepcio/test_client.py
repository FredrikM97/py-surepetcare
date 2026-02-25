import aresponses
import pytest
from surepcio import SurePetcareClient
from surepcio.command import Command


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
        result = await client.api(Command("GET", "https://example.com/endpoint"))
        assert result is None


@pytest.mark.asyncio
async def test_async_put_with_pending_and_polling(
    aresponses: aresponses.ResponsesMockServer, mock_api_device
):
    """Test async PUT operation with pending results that completes via polling."""
    # Mock PUT response with pending status (status_id=5)
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/device/123/control",
        "PUT",
        aresponses.Response(
            text='{"data": {"id": 123, "control": {}}, "pending": [{"request_id": "abc", "status_id": 5}]}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    # Mock polling response (status changed to 0=completed)
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/household/7777/device/control/status",
        "GET",
        aresponses.Response(
            text='{"results": [{"request_id": "abc", "status_id": 0}]}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    # Mock device refresh
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/device/123",
        "GET",
        aresponses.Response(
            text='{"data": {"id": 123, "control": {"bowls": null}, "status": {}, "household_id": 7777}}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with SurePetcareClient() as client:
        device = mock_api_device
        device.id = 123
        device.household_id = 7777
        device.controlCls = dict
        device.statusCls = dict
        device.refresh.return_value = Command("GET", "https://app-api.production.surehub.io/api/device/123")

        cmd = Command(
            method="PUT",
            endpoint="https://app-api.production.surehub.io/api/device/123/control",
            device=device,
        )
        result = await client.api(cmd)
        assert result is not None


@pytest.mark.asyncio
async def test_non_async_put_updates_device(aresponses: aresponses.ResponsesMockServer, mock_api_device):
    """Test non-async PUT updates device control directly."""
    # Mock PUT response with completed status (status_id=0)
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/device/456/control",
        "PUT",
        aresponses.Response(
            text=(
                '{"data": {"id": 456, "control": {"bowls": {"type": 1}}, '
                '"status": {"online": true}}, "pending": '
                '[{"request_id": "xyz", "status_id": 0}]}'
            ),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    # Mock refresh endpoint
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/device/456",
        "GET",
        aresponses.Response(
            text='{"data": {"id": 456, "control": {"bowls": {"type": 1}}, "status": {"online": true}}}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with SurePetcareClient() as client:
        device = mock_api_device
        device.id = 456
        device.refresh.return_value = Command("GET", "https://app-api.production.surehub.io/api/device/456")

        cmd = Command(
            method="PUT",
            endpoint="https://app-api.production.surehub.io/api/device/456/control",
            device=device,
        )
        result = await client.api(cmd)
        assert result is not None


@pytest.mark.asyncio
async def test_async_post_with_device_refresh(aresponses: aresponses.ResponsesMockServer, mock_api_device):
    """Test async POST operation with pending results."""
    # Mock POST response with pending status
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/device/789/control",
        "POST",
        aresponses.Response(
            text='{"data": {}, "pending": [{"request_id": "post1", "status_id": 5}]}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    # Mock polling response (completed)
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/household/8888/device/control/status",
        "GET",
        aresponses.Response(
            text='{"results": [{"request_id": "post1", "status_id": 0}]}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    # Mock device refresh
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/device/789",
        "GET",
        aresponses.Response(
            text='{"data": {"id": 789, "control": {}, "status": {}, "household_id": 8888}}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with SurePetcareClient() as client:
        device = mock_api_device
        device.id = 789
        device.household_id = 8888
        device.controlCls = dict
        device.statusCls = dict
        device.refresh.return_value = Command("GET", "https://app-api.production.surehub.io/api/device/789")

        cmd = Command(
            method="POST",
            endpoint="https://app-api.production.surehub.io/api/device/789/control",
            device=device,
        )
        result = await client.api(cmd)
        assert result is not None
