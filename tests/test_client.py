import asyncio

import pytest

from surepetcare.client import SurePetcareClient


class DummyResponse:
    def __init__(self, ok=True, status=200, text="OK", json_data=None):
        self.ok = ok
        self.status = status
        self._text = text
        self._json_data = json_data or {"foo": "bar"}

    async def text(self):
        return self._text

    async def json(self):
        return self._json_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class DummySession:
    def __init__(self, ok=True, status=200, text="OK", json_data=None):
        self._ok = ok
        self._status = status
        self._text = text
        self._json_data = json_data or {"foo": "bar"}

    def get(self, *args, **kwargs):
        return DummyResponse(self._ok, self._status, self._text, self._json_data)

    def post(self, *args, **kwargs):
        return DummyResponse(self._ok, self._status, self._text, self._json_data)


def test_get_success():
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"

    async def run():
        result = await client.get("/endpoint")
        assert result == {"foo": "bar"}

    asyncio.run(run())


def test_get_error():
    client = SurePetcareClient()
    client.session = DummySession(ok=False, status=404, text="Not found")
    client._token = "dummy-token"

    async def run():
        with pytest.raises(Exception):
            await client.get("/endpoint")

    asyncio.run(run())


def test_post_success():
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"

    async def run():
        result = await client.post("/endpoint", data={})
        assert result == {"foo": "bar"}

    asyncio.run(run())


def test_post_error():
    client = SurePetcareClient()
    client.session = DummySession(ok=False, status=400, text="Bad request")
    client._token = "dummy-token"

    async def run():
        with pytest.raises(Exception):
            await client.post("/endpoint", data={})

    asyncio.run(run())


def test_post_204():
    class DummySession204(DummySession):
        def post(self, *args, **kwargs):
            return DummyResponse(ok=True, status=204, text="", json_data={})

    client = SurePetcareClient()
    client.session = DummySession204()
    client._token = "dummy-token"

    async def run():
        result = await client.post("/endpoint", data={})
        assert result == {}

    asyncio.run(run())


@pytest.mark.asyncio
async def test_get_raises_on_error():
    class DummySession:
        async def get(self, *args, **kwargs):
            class DummyResponse:
                ok = False
                status = 404

                async def text(self):
                    return "Not found"

            return DummyResponse()

    client = SurePetcareClient()
    client.session = DummySession()
    with pytest.raises(Exception):
        await client.get("http://dummy/endpoint")


@pytest.mark.asyncio
async def test_post_raises_on_error():
    class DummySession:
        async def post(self, *args, **kwargs):
            class DummyResponse:
                ok = False
                status = 400

                async def text(self):
                    return "Bad request"

            return DummyResponse()

    client = SurePetcareClient()
    client.session = DummySession()
    with pytest.raises(Exception):
        await client.post("http://dummy/endpoint", data={})
