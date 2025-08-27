import pytest

from surepetcare.security.auth import AuthClient
from tests.mock_helpers import DummySession


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "json_data",
    [
        {"error": "invalid credentials"},
        {"data": {}},
    ],
)
async def test_login_failure(json_data):
    """Test login failure raises Exception and token is not set."""
    client = AuthClient()
    client.session = DummySession(ok=False, status=401, json_data=json_data)
    with pytest.raises(Exception):
        await client.login("user@example.com", "wrongpassword")
    with pytest.raises(Exception):
        _ = client.token


@pytest.mark.asyncio
async def test_login_token_device_id():
    """Test login with token and device_id sets both."""
    client = AuthClient()
    client.session = DummySession(ok=True, status=200, json_data={"data": {"token": "tok"}})
    result = await client.login(token="tok", device_id="dev")
    assert client._token == "tok"
    assert client._device_id == "dev"
    assert result is client


@pytest.mark.asyncio
async def test_login_missing_credentials():
    """Test login raises if no credentials provided."""
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
    # Do not pass token as a keyword argument
    headers = client._generate_headers()
    assert "X-Device-Id" in headers


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


def test_token_missing_error_message():
    client = AuthClient()
    with pytest.raises(Exception, match="Authentication token is missing"):
        _ = client.token


def test_device_id_missing_error_message():
    client = AuthClient()
    with pytest.raises(Exception, match="Device ID is missing"):
        _ = client.device_id


def test_del_warns(monkeypatch):
    import warnings

    client = AuthClient()

    class DummySession:
        closed = False

    client.session = DummySession()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        del client
        assert any("was deleted without closing the aiohttp session" in str(warn.message) for warn in w)
