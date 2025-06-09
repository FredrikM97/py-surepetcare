import json
import os
from typing import Any
from typing import Optional

from surepetcare.client import SurePetcareClient


def load_mock_data(filepath):
    """Load and return JSON data from a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Mock data file not found: {filepath}")
    with open(filepath) as f:
        return json.load(f)


class MockSurePetcareClient(SurePetcareClient):
    def __init__(self, mock_get_data=None):
        super().__init__()
        self.mock_get_data = mock_get_data or {}

    async def get(self, endpoint: str, params: Optional[dict[Any, Any]] = None):
        # If the value is a string, treat it as a filename and load JSON
        if isinstance(self.mock_get_data, str):
            return load_mock_data(self.mock_get_data)
        return self.mock_get_data.get(endpoint, {})

    async def post(self, endpoint: str, data: Optional[dict[Any, Any]] = None):
        # Implement as needed
        return {}


class DummyUrl:
    def __init__(self, path):
        self.path = path


class DummyResponse:
    def __init__(self, ok=True, status=200, json_data=None, path="/endpoint", text=None):
        self.ok = ok
        self.status = status
        self._json_data = json_data or {}
        self.headers = {}
        self.url = DummyUrl(path)
        self.text = text or "OK"

    def get(self, key, default=None):
        return self._json_data.get(key, default)

    async def json(self):
        return self._json_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class DummySession:
    def __init__(self, ok=True, status=200, text="OK", json_data=None, method=None):
        self._ok = ok
        self._status = status
        self._text = text
        self._json_data = json_data or {"foo": "bar"}
        self._closed = False
        # 'method' is accepted for compatibility but not used

    @property
    def closed(self):
        return self._closed

    def get(self, *args, response=None, **kwargs):
        resp = response or DummyResponse(
            ok=self._ok, status=self._status, text=self._text, json_data=self._json_data
        )

        class AsyncContextManager:
            async def __aenter__(self_inner):
                return resp

            async def __aexit__(self_inner, exc_type, exc, tb):
                pass

        return AsyncContextManager()

    def post(self, *args, response=None, **kwargs):
        resp = response or DummyResponse(
            ok=self._ok, status=self._status, text=self._text, json_data=self._json_data
        )

        class AsyncContextManager:
            async def __aenter__(self_inner):
                return resp

            async def __aexit__(self_inner, exc_type, exc, tb):
                pass

        return AsyncContextManager()

    def request(self, *args, response=None, **kwargs):
        resp = response or DummyResponse(
            ok=self._ok, status=self._status, text=self._text, json_data=self._json_data
        )

        class AsyncContextManager:
            async def __aenter__(self_inner):
                return resp

            async def __aexit__(self_inner, exc_type, exc, tb):
                pass

        return AsyncContextManager()

    async def close(self):
        self._closed = True
