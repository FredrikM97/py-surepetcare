import pytest

from surepetcare.client import SurePetcareClient
from tests.mock_helpers import DummySession
from tests.mock_helpers import MockClient


@pytest.fixture
def client_file():
    return "tests/fixture/test_client.json"


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [204, 304])
async def test_get_none_status(status, client_file):
    """Test GET returns None for 204/304 status."""
    client = MockClient(client_file)
    client.session = DummySession(ok=True, status=status)
    # {"/endpoint": {"foo": "bar"}}
    client._token = "dummy-token"
    result = await client.get("/endpoint")
    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("ok,status", [(False, 404), (False, 400)])
async def test_get_and_post_raises_on_error(ok, status):
    """Test GET/POST raises on error status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=ok, status=status)
    client.session._json_data = {"/endpoint": {"foo": "bar"}}
    client._token = "dummy-token"
    with pytest.raises(Exception):
        await client.get("/endpoint")
    with pytest.raises(Exception):
        await client.post("/endpoint", data={})


@pytest.mark.asyncio
async def test_api_not_implemented():
    """Test api() raises for unsupported method."""
    client = SurePetcareClient()

    class DummyCommand:
        method = "put"
        endpoint = "/endpoint"
        params = None
        reuse = True
        callback = None

    with pytest.raises(NotImplementedError):
        await client.api(DummyCommand())


@pytest.mark.asyncio
async def test_api_callback_none(client_file):
    """Test api() returns JSON if callback is None."""
    client = MockClient(client_file)
    client._token = "dummy-token"

    class DummyCommand:
        method = "get"
        endpoint = "/endpoint"
        params = None
        reuse = True
        callback = None

    result = await client.api(DummyCommand())
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_api_post(client_file):
    """Test api() POST returns JSON."""
    client = MockClient(client_file)
    client._token = "dummy-token"

    class DummyCommand:
        method = "post"
        endpoint = "/endpoint"
        params = {"bar": 1}
        reuse = True
        callback = None

    result = await client.api(DummyCommand())
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_api_callback_custom(client_file):
    """Test api() with custom callback returns expected value."""
    client = MockClient(client_file)
    client._token = "dummy-token"

    class DummyCommand:
        method = "get"
        endpoint = "/endpoint"
        params = None
        reuse = True
        callback = staticmethod(lambda resp: resp["foo"])

    result = await client.api(DummyCommand())
    assert result == "bar"


@pytest.mark.asyncio
async def test_api_callback_raises(client_file):
    """Test api() raises if callback raises."""
    client = MockClient(client_file)

    class DummyCommand:
        method = "get"
        endpoint = "/endpoint"
        params = None
        reuse = True
        # Callback raises an error
        callback = staticmethod(lambda resp: (_ for _ in ()).throw(ValueError("callback error")))

    with pytest.raises(ValueError, match="callback error"):
        await client.api(DummyCommand())


@pytest.mark.asyncio
async def test_api_method_case_insensitive(client_file):
    """Test api() accepts uppercase method names."""
    client = MockClient(client_file)
    client._token = "dummy-token"

    class DummyCommand:
        method = "GET"  # uppercase
        endpoint = "/endpoint"
        params = None
        reuse = True
        callback = None

    result = await client.api(DummyCommand())
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_api_post_with_params(client_file):
    """Test api() POST with params returns JSON."""
    client = MockClient(client_file)
    client._token = "dummy-token"

    class DummyCommand:
        method = "post"
        endpoint = "/endpoint"
        params = {"bar": 1}
        reuse = True
        callback = None

    result = await client.api(DummyCommand())
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_api_callback_returns_none(client_file):
    """Test api() returns None if callback returns None."""
    client = MockClient(client_file)
    client._token = "dummy-token"

    class DummyCommand:
        method = "get"
        endpoint = "/endpoint"
        params = None
        reuse = True
        callback = staticmethod(lambda resp: None)

    result = await client.api(DummyCommand())
    assert result is None
