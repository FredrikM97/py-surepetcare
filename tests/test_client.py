import pytest

from surepetcare.client import SurePetcareClient
from tests.mock_helpers import DummySession


class DummyUrl:
    def __init__(self, path):
        self.path = path


class DummyResponse:
    def __init__(self, ok=True, status=200, json_data=None, path="/endpoint"):
        self.ok = ok
        self.status = status
        self._json_data = json_data or {}
        self.url = DummyUrl(path)

    async def json(self):
        return self._json_data

    async def text(self):
        return str(self._json_data)


@pytest.mark.asyncio
async def test_get_204():
    """Test GET returns None for 204 status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=204)
    client._token = "dummy-token"
    result = await client.get("/endpoint")
    assert result is None


@pytest.mark.asyncio
async def test_get_304():
    """Test GET returns None for 304 status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=304)
    client._token = "dummy-token"
    result = await client.get("/endpoint")
    assert result is None


@pytest.mark.asyncio
async def test_get_success():
    """Test GET returns JSON for 200 status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"
    result = await client.get("/endpoint")
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_post_success():
    """Test POST returns JSON for 200 status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"
    result = await client.post("/endpoint", data={})
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_post_204():
    """Test POST returns only status for 204 status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=204, json_data={})
    client._token = "dummy-token"
    result = await client.post("/endpoint", data={})
    assert result == {"status": 204}
    await client.session.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("ok,status,raises", [
    (False, 404, Exception),
    (False, 400, Exception),
])
async def test_get_and_post_raises_on_error(ok, status, raises):
    """Test GET/POST raises on error status."""
    client = SurePetcareClient()
    client.session = DummySession(ok=ok, status=status, text="Error")
    client._token = "dummy-token"
    with pytest.raises(raises):
        await client.get("http://dummy/endpoint")
    with pytest.raises(raises):
        await client.post("http://dummy/endpoint", data={})


@pytest.mark.asyncio
async def test_api_callback():
    """Test api() uses callback if provided."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
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
async def test_api_callback_none():
    """Test api() returns JSON if callback is None."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
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
async def test_api_post():
    """Test api() POST returns JSON."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
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
async def test_api_callback_custom():
    """Test api() with custom callback returns expected value."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
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
async def test_api_callback_raises():
    """Test api() raises if callback raises."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"

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
async def test_api_method_case_insensitive():
    """Test api() accepts uppercase method names."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
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
async def test_api_post_with_params():
    """Test api() POST with params returns JSON."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
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
async def test_api_callback_returns_none():
    """Test api() returns None if callback returns None."""
    client = SurePetcareClient()
    client.session = DummySession(ok=True, status=200, json_data={"foo": "bar"})
    client._token = "dummy-token"

    class DummyCommand:
        method = "get"
        endpoint = "/endpoint"
        params = None
        reuse = True
        callback = staticmethod(lambda resp: None)

    result = await client.api(DummyCommand())
    assert result is None
