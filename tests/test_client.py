import pytest

from surepy.client import SurePetcareClient


@pytest.mark.asyncio
async def test_get_raises_on_error(monkeypatch):
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
async def test_post_raises_on_error(monkeypatch):
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
