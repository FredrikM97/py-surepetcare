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


@pytest.mark.skip(reason="Temporarily disabled. Missing functionality in aresponses?")
@pytest.mark.asyncio
async def test_api_put(aresponses: aresponses.ResponsesMockServer):
    aresponses.add(
        "example.com",
        "/endpoint",
        "PUT",
        aresponses.Response(
            text='{"data": {"foo": "bar"}}', status=200, headers={"Content-Type": "application/json"}
        ),
    )
    async with SurePetcareClient() as client:
        result = await client.api(Command("PUT", "https://example.com/endpoint", params={"bar": 1}))
        assert result == {"data": {"foo": "bar"}}


@pytest.mark.skip(reason="Temporarily disabled. Missing functionality in aresponses?")
@pytest.mark.asyncio
async def test_api_delete(aresponses: aresponses.ResponsesMockServer):
    aresponses.add(
        "example.com",
        "/endpoint",
        "DELETE",
        aresponses.Response(
            text='{"data": {"foo": "bar"}}', status=200, headers={"Content-Type": "application/json"}
        ),
    )
    async with SurePetcareClient() as client:
        result = await client.api(Command("DELETE", "https://example.com/endpoint", full_response=True))
        assert result == {"data": {"foo": "bar"}}


@pytest.mark.skip(reason="Temporarily disabled. Missing functionality in aresponses?")
@pytest.mark.asyncio
async def test_api_post(aresponses: aresponses.ResponsesMockServer):
    aresponses.add(
        "example.com",
        "/endpoint",
        "POST",
        aresponses.Response(
            text='{"data": {"foo": "bar"}}', status=200, headers={"Content-Type": "application/json"}
        ),
    )
    async with SurePetcareClient() as client:
        result = await client.api(
            Command(method="POST", endpoint="https://example.com/endpoint", params={"bar": 1})
        )
        assert result == {"data": {"foo": "bar"}}
