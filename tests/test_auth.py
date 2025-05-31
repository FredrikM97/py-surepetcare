import pytest

from surepetcare.security.auth import AuthClient
from tests.mock_helpers import DummySession


@pytest.mark.asyncio
async def test_login_success():
    client = AuthClient()
    client.session = DummySession(ok=True, status=200, json_data={"data": {"token": "dummy-token"}})
    result = await client.login("user@example.com", "password")
    assert client._token == "dummy-token"
    assert result is client


@pytest.mark.asyncio
async def test_login_failure():
    client = AuthClient()
    client.session = DummySession(ok=False, status=401, json_data={"error": "invalid credentials"})
    with pytest.raises(Exception):
        await client.login("user@example.com", "wrongpassword")


@pytest.mark.asyncio
async def test_login_failure_and_token_not_found():
    client = AuthClient()
    client.session = DummySession(ok=False, status=401, json_data={"error": "invalid credentials"})
    with pytest.raises(Exception):
        await client.login("user@example.com", "wrongpassword")
    with pytest.raises(Exception):
        client.token


@pytest.mark.asyncio
async def test_login_token_device_id():
    client = AuthClient()
    client.session = DummySession(ok=True, status=200, json_data={"data": {"token": "tok"}})
    result = await client.login(token="tok", device_id="dev")
    assert client._token == "tok"
    assert client._device_id == "dev"
    assert result is client


@pytest.mark.asyncio
async def test_login_missing_credentials():
    client = AuthClient()
    client.session = DummySession(ok=True, status=200, json_data={"data": {"token": "tok"}})
    with pytest.raises(Exception):
        await client.login()


@pytest.mark.asyncio
async def test_login_success_but_token_missing():
    client = AuthClient()
    client.session = DummySession(ok=True, status=200, json_data={"data": {}})
    with pytest.raises(Exception, match="Token not found"):
        await client.login("user@example.com", "password")


def test_generate_headers():
    client = AuthClient()
    client._device_id = "dev"
    headers = client._generate_headers(token="tok")
    assert isinstance(headers, dict)
    assert any("tok" in v for v in headers.values())


def test_token_success():
    client = AuthClient()
    client._token = "tok"
    assert client.token == "tok"


def test_token_missing():
    client = AuthClient()
    with pytest.raises(Exception):
        client.token


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
    class DummyWithClosed:
        @property
        def closed(self):
            return False

    s = DummyWithClosed()
    client.session = s
    await client.set_session()
    assert client.session is s
