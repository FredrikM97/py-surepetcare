import pytest

from surepcio.const import API_ENDPOINT_PRODUCTION
from surepcio.security.auth import AuthClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "json_data, status",
    [
        ({"error": "invalid credentials"}, 401),
        ({"data": {}}, 401),
    ],
)
async def test_login_failure(aresponses, json_data, status):
    aresponses.add(
        API_ENDPOINT_PRODUCTION,
        "/auth/login",
        "POST",
        aresponses.Response(
            text='{"error": "invalid credentials"}',
            status=status,
            headers={"Content-Type": "application/json"},
        ),
    )
    client = AuthClient()
    with pytest.raises(Exception):
        await client.login("user@example.com", "wrongpassword")
    with pytest.raises(Exception):
        _ = client.token


@pytest.mark.asyncio
async def test_login_token_device_id(aresponses):
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/auth/login",
        "POST",
        aresponses.Response(
            text='{"data": {"token": "tok"}}', status=200, headers={"Content-Type": "application/json"}
        ),
    )
    client = AuthClient()
    result = await client.login(token="tok", device_id="dev")
    assert client._token == "tok"
    assert client._device_id == "dev"
    assert result is client


@pytest.mark.asyncio
async def test_login_missing_credentials(aresponses):
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/auth/login",
        "POST",
        aresponses.Response(
            text='{"data": {"token": "tok"}}', status=200, headers={"Content-Type": "application/json"}
        ),
    )
    client = AuthClient()
    with pytest.raises(Exception):
        await client.login()


@pytest.mark.asyncio
async def test_login_success_but_token_missing(aresponses):
    aresponses.add(
        "app-api.production.surehub.io",
        "/api/auth/login",
        "POST",
        aresponses.Response(text='{"data": {}}', status=200, headers={"Content-Type": "application/json"}),
    )
    client = AuthClient()
    with pytest.raises(Exception, match="Token not found in response"):
        await client.login("user@example.com", "password")


def test_generate_headers():
    client = AuthClient()
    client._device_id = "dev"
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
    from surepcio.security.auth import get_formatted_header

    h = get_formatted_header(user_agent="ua", token="tok", device_id="dev")
    assert isinstance(h, dict)
    assert all(isinstance(k, str) for k in h)


@pytest.mark.asyncio
async def test_close_with_and_without_session():
    client = AuthClient()
    # No session
    await client.close()

    # With session
    await client.set_session()
    await client.close()
    assert client.session.closed


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

    # Simulate a session that is not closed
    class DummySession:
        closed = False

    client.session = DummySession()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        del client
        assert any("was deleted without closing the aiohttp session" in str(warn.message) for warn in w)
