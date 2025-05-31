import pytest

from surepetcare.client import SurePetcareClient
from tests.mock_helpers import DummySession


async def test_get_success():
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"
    result = await client.get("/endpoint")
    assert result == {"foo": "bar"}


async def test_get_error():
    client = SurePetcareClient()
    client.session = DummySession(ok=False, status=404, text="Not found")
    client._token = "dummy-token"
    with pytest.raises(Exception):
        await client.get("/endpoint")


async def test_post_success():
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"
    result = await client.post("/endpoint", data={})
    assert result == {"foo": "bar"}


async def test_post_error():
    client = SurePetcareClient()
    client.session = DummySession(ok=False, status=400, text="Bad request")
    client._token = "dummy-token"
    with pytest.raises(Exception):
        await client.post("/endpoint", data={})


async def test_post_204():
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=204, json_data={})
    client._token = "dummy-token"
    result = await client.post("/endpoint", data={})
    assert result == {}
    await client.session.close()


async def test_get_raises_on_error():
    client = SurePetcareClient()
    client.session = DummySession(ok=False, status=404, text="Not found")
    client._token = "dummy-token"
    with pytest.raises(Exception):
        await client.get("http://dummy/endpoint")


async def test_post_raises_on_error():
    client = SurePetcareClient()
    client.session = DummySession(ok=False, status=400, text="Bad request")
    client._token = "dummy-token"
    with pytest.raises(Exception):
        await client.post("http://dummy/endpoint", data={})
