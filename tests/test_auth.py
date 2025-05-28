import pytest

from surepetcare.security.auth import AuthClient


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


@pytest.mark.asyncio
async def test_login_failure_and_token_not_found():
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
    # login should fail and token should not be set
    with pytest.raises(Exception):
        await client.login("user@example.com", "wrongpassword")
    with pytest.raises(Exception):
        client.get_token()


@pytest.mark.asyncio
async def test_login_token_device_id():
    client = AuthClient()
    client.session = object()  # Dummy, won't be used
    result = await client.login(token="tok", device_id="dev")
    assert client._token == "tok"
    assert client._device_id == "dev"
    assert result is client


@pytest.mark.asyncio
async def test_login_missing_credentials():
    client = AuthClient()
    client.session = object()
    with pytest.raises(Exception):
        await client.login()


def test_generate_headers():
    client = AuthClient()
    client._device_id = "dev"
    headers = client._generate_headers(token="tok")
    assert isinstance(headers, dict)
    assert any("tok" in v for v in headers.values())


def test_get_token_success():
    client = AuthClient()
    client._token = "tok"
    assert client.get_token() == "tok"


def test_get_token_missing():
    client = AuthClient()
    with pytest.raises(Exception):
        client.get_token()


def test_get_formatted_header():
    from surepetcare.security.auth import get_formatted_header

    h = get_formatted_header(user_agent="ua", token="tok", device_id="dev")
    assert isinstance(h, dict)
    assert all(isinstance(k, str) for k in h)


@pytest.mark.asyncio
async def test_close_with_and_without_session():
    client = AuthClient()
    # No session
    await client.close()

    # With session
    class DummySession:
        closed = False

        async def close(self):
            DummySession.closed = True

    client.session = DummySession()
    await client.close()
    assert DummySession.closed


@pytest.mark.asyncio
async def test_set_session():
    client = AuthClient()
    await client.set_session()
    assert client.session is not None
    # Should not overwrite if already set
    s = object()
    client.session = s
    await client.set_session()
    assert client.session is s


@pytest.mark.asyncio
async def test_login_success_but_token_missing():
    class DummyResponse:
        status = 200

        async def json(self):
            return {"data": {}}  # No token in response

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class DummySession:
        def request(self, *args, **kwargs):
            return DummyResponse()

    client = AuthClient()
    client.session = DummySession()
    with pytest.raises(Exception, match="Token not found"):
        await client.login("user@example.com", "password")
