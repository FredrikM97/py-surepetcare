import pytest

from surepy.security.auth import AuthClient


@pytest.mark.asyncio
async def test_login_success():
    class DummyResponse:
        status = 200

        async def json(self):
            return {"data": {"token": "dummy-token"}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class DummySession:
        def request(self, *args, **kwargs):
            return DummyResponse()

    client = AuthClient()
    client.session = DummySession()
    result = await client.login("user@example.com", "password")
    assert client._token == "dummy-token"
    assert result is client


@pytest.mark.asyncio
async def test_login_failure():
    class DummyResponse:
        status = 401

        async def json(self):
            return {"error": "invalid credentials"}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class DummySession:
        def request(self, *args, **kwargs):
            return DummyResponse()

    client = AuthClient()
    client.session = DummySession()
    with pytest.raises(Exception):
        await client.login("user@example.com", "wrongpassword")
