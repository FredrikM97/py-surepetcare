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

    async def get(self, endpoint: str, params: Optional[dict[Any, Any]] = None, headers=None):
        # If the value is a string, treat it as a filename and load JSON
        if isinstance(self.mock_get_data, str):
            return load_mock_data(self.mock_get_data)
        # Always return a dict with 'status' for compatibility with real client
        data = self.mock_get_data.get(endpoint, None)
        if data is None:
            # Only use fallback if no mock is provided
            if "/product/" in endpoint:
                data = {"data": {"foo": "bar"}}
            elif endpoint.endswith("/pet") or endpoint.endswith("/dashboard/pet"):
                data = {"data": []}
            elif endpoint.endswith("/device"):
                data = {
                    "data": [
                        {
                            "id": 10,
                            "household_id": 1,
                            "name": "Hub1",
                            "product_id": 1,
                            "status": {"online": True},
                            "control": {},
                        },
                        {
                            "id": 11,
                            "household_id": 1,
                            "name": "Feeder1",
                            "product_id": 4,
                            "status": {"online": True},
                            "control": {
                                "lid": {"close_delay": 5},
                                "bowls": {
                                    "settings": [
                                        {
                                            "food_type": 1,
                                            "substance_type": 0,
                                            "current_weight": 0.0,
                                            "last_filled_at": "",
                                            "last_zeroed_at": "",
                                            "fill_percent": 0,
                                        },
                                        {
                                            "food_type": 2,
                                            "substance_type": 0,
                                            "current_weight": 0.0,
                                            "last_filled_at": "",
                                            "last_zeroed_at": "",
                                            "fill_percent": 0,
                                        },
                                    ]
                                },
                            },
                        },
                    ]
                }
            elif "/device/" in endpoint or endpoint.endswith("/aggregate"):
                data = {
                    "data": {
                        "id": 1,
                        "household_id": 1,
                        "name": "Feeder1",
                        "product_id": 4,
                        "status": {
                            "online": True,
                            "bowl_status": [
                                {
                                    "index": 0,
                                    "food_type": 1,
                                    "substance_type": 0,
                                    "current_weight": 0.0,
                                    "last_filled_at": "",
                                    "last_zeroed_at": "",
                                    "fill_percent": 0,
                                },
                                {
                                    "index": 1,
                                    "food_type": 1,
                                    "substance_type": 0,
                                    "current_weight": 0.0,
                                    "last_filled_at": "",
                                    "last_zeroed_at": "",
                                    "fill_percent": 0,
                                },
                            ],
                        },
                        "control": {
                            "lid": {"close_delay": 5},
                            "bowls": {
                                "settings": [
                                    {
                                        "food_type": 1,
                                        "substance_type": 0,
                                        "current_weight": 0.0,
                                        "last_filled_at": "",
                                        "last_zeroed_at": "",
                                        "fill_percent": 0,
                                    },
                                    {
                                        "food_type": 1,
                                        "substance_type": 0,
                                        "current_weight": 0.0,
                                        "last_filled_at": "",
                                        "last_zeroed_at": "",
                                        "fill_percent": 0,
                                    },
                                ]
                            },
                        },
                    }
                }
            elif "/household/" in endpoint:
                data = {"data": {"id": 1, "name": "TestHouse"}}
            else:
                data = {"data": {}}
        if "status" not in data:
            data["status"] = 200
        return data

    async def post(
        self, endpoint: str, data: dict[Any, Any] | None = None, headers=None, reuse=True
    ) -> dict[Any, Any]:
        # Return mock data if available, else default
        mock = self.mock_get_data.get(endpoint) if isinstance(self.mock_get_data, dict) else None
        if mock and isinstance(mock, dict) and "data" in mock:
            # Simulate a real response: merge data and status
            result = dict(mock["data"])
            result["status"] = 200
            return result
        # Default fallback
        return {"foo": "bar", "status": 200}


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
