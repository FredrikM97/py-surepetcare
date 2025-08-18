import json
import os

from surepetcare.client import SurePetcareClient


def load_mock_data(filepath):
    """Load and return JSON data from a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Mock data file not found: {filepath}")
    with open(filepath) as f:
        return json.load(f)


def recursive_dump(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_none=True)
    elif isinstance(obj, dict):
        return {k: recursive_dump(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_dump(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        return {k: recursive_dump(v) for k, v in obj.__dict__.items()}
    else:
        return obj


def patch_client_get(return_value):
    client = SurePetcareClient()

    async def fake_get(*args, **kwargs):
        return return_value

    client.get = fake_get
    return client


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


def make_pet():
    from surepetcare.devices.pet import Pet

    return Pet({"id": 2, "household_id": 1, "name": "N", "tag": {"id": 3}})
