import enum
import inspect
import json
from pathlib import Path
from unittest.mock import ANY, MagicMock
from urllib.parse import urlparse
import warnings
import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion

from surepcio.const import API_ENDPOINT_PRODUCTION
from tests import FIXTURES


def _load_device(device_name: str) -> dict:
    path = Path(f"tests/fixture/{device_name}.json")
    if not path.exists():
        raise FileNotFoundError(f"Fixture file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
        return data


@pytest.fixture
def mock_device(device_name: str) -> dict:
    return _load_device(device_name)


@pytest.fixture
def mock_all_devices() -> list[dict]:
    return [_load_device(device_name) for device_name in FIXTURES]


@pytest.fixture
def mock_devices(device_names) -> list[dict]:
    return [_load_device(device_name) for device_name in device_names]


@pytest.fixture
def mock_api_device() -> MagicMock:
    """Create a mock device for testing API operations."""

    class MockControl:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class MockStatus:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    device = MagicMock()
    device.controlCls = MockControl
    device.statusCls = MockStatus
    return device


class ApiMockServer:
    """Wraps an aresponses server with a higher-level API for registering JSON responses.

    Raises ``ValueError`` when a route is registered twice without ``overwrite=True``,
    making fixture conflicts immediately visible rather than silently serving stale data.
    """

    def __init__(self, server: aresponses.ResponsesMockServer) -> None:
        self._server = server

    @staticmethod
    def _parse_endpoint(endpoint: str) -> tuple[str, str]:
        """Return (host, path) from a full URL or a bare path relative to the production API."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            parsed = urlparse(endpoint)
            path = parsed.path
            if parsed.query:
                path += "?" + parsed.query
            return parsed.netloc, path
        return urlparse(API_ENDPOINT_PRODUCTION).netloc, endpoint

    def _existing_routes(self, host: str, path: str, method: str) -> list:
        """Return all registered routes that match the given host, path, and method."""
        return [
            (r, res)
            for r, res in self._server._responses
            if r.host_pattern == host.lower()
            and r.path_pattern == path
            and r.method_pattern == method.lower()
        ]

    def __call__(
        self,
        method: str,
        endpoint: str,
        payload: dict,
        status: int = 200,
        match_querystring: bool = False,
        repeat: int = 50,
        overwrite: bool = False,
    ) -> None:
        host, path = self._parse_endpoint(endpoint)
        existing: list = self._existing_routes(host, path, method)

        if overwrite:
            self._server._responses[:] = [
                (r, res)
                for r, res in self._server._responses
                if (r, res) not in existing
            ]
        elif existing:
            warnings.warn(
                f"Route already registered: {method} {host}{path} — queuing another response.",
                stacklevel=2,
            )
        self._server.add(
            host,
            path,
            method,
            self._server.Response(
                body=json.dumps(payload),
                status=status,
                headers={"Content-Type": "application/json"},
            ),
            match_querystring=match_querystring,
            repeat=repeat,
        )


@pytest.fixture
def register_device_api_mocks(add_api_json_response):
    def _register(mock_devices: list[dict]):
        for method_dict in mock_devices:
            for method, device in method_dict.items():
                for url, payload in device.items():
                    add_api_json_response(method, url, payload, match_querystring=True)

    return _register


@pytest.fixture
def add_api_json_response(aresponses: aresponses.ResponsesMockServer) -> ApiMockServer:
    """Fixture returning an ``ApiMockServer`` pre-bound to the active aresponses server.

    Tests call it directly:  ``add_api_json_response("GET", "/some/path", {...})``
    Pass ``overwrite=True`` to replace an already-registered route for the same endpoint.
    """
    return ApiMockServer(aresponses)


def mask_fields(obj, skip_fields=None, any_fields=None):
    skip_fields = skip_fields or set()
    any_fields = any_fields or set()
    if isinstance(obj, dict):
        return {
            k: (ANY if k in any_fields else mask_fields(v, skip_fields, any_fields))
            for k, v in obj.items()
            if k not in skip_fields
        }
    elif isinstance(obj, (list, tuple, set)):
        return type(obj)(mask_fields(v, skip_fields, any_fields) for v in obj)
    else:
        return obj


def serialize(obj):
    if hasattr(obj, "model_dump"):
        return serialize(dict(obj))
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [serialize(item) for item in obj]
    elif isinstance(obj, enum.Enum):
        return obj  # or obj.name if you prefer
    elif hasattr(obj, "__dict__"):
        data = {k: serialize(v) for k, v in vars(obj).items() if not k.startswith("_")}
        # Add public properties
        properties = {}
        for name, member in inspect.getmembers(type(obj)):
            if isinstance(member, property) and not name.startswith("_"):
                try:
                    properties[name] = serialize(getattr(obj, name))
                except Exception:
                    properties[name] = "<error>"
        if properties:
            data["properties"] = properties
        return data
    else:
        return obj


def object_snapshot(
    data, snapshot: SnapshotAssertion, skip_fields=None, any_fields=None
):
    data = mask_fields(
        data,
        skip_fields=skip_fields,
        any_fields=any_fields,
    )
    assert serialize(data) == snapshot
