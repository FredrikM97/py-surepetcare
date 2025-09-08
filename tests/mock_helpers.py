import json

from surepcio.client import SurePetcareClient


def load_mock_data_for_endpoint(fixture_file="tests/fixture/pet.json"):
    with open(fixture_file) as f:
        data = json.load(f)
    return data


class MockClient(SurePetcareClient):
    def __init__(self, fixture_file, modify_hook=None):
        super().__init__()
        self.fixture_file = fixture_file
        self.modify_hook = modify_hook
        self.session = DummySession()  # Use your DummySession
        self.set_mock_response()

    def set_mock_response(self, file=None):
        mock_data = load_mock_data_for_endpoint(self.fixture_file if file is None else file)
        if self.modify_hook:
            mock_data = self.modify_hook(mock_data)
        self.session._json_data = mock_data

    def reset(self):
        self.set_mock_response(self.fixture_file)


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
    def __init__(self, ok=True, status=200, text="OK", json_data=None):
        self._ok = ok
        self._status = status
        self._text = text
        self._json_data = json_data
        self._closed = False

    @property
    def closed(self):
        return self._closed

    def _get_response(self, endpoint=None, response=None):
        json_data = self._json_data
        if endpoint is not None and isinstance(json_data, dict):
            if endpoint in json_data:
                resp = DummyResponse(
                    ok=self._ok, status=self._status, text=self._text, json_data=json_data[endpoint]
                )
            else:
                raise KeyError(f"Mock data for endpoint '{endpoint}' not found in fixture.")
        else:
            resp = response or DummyResponse(
                ok=self._ok, status=self._status, text=self._text, json_data=json_data
            )

        class AsyncContextManager:
            async def __aenter__(self_inner):
                return resp

            async def __aexit__(self_inner, exc_type, exc, tb):
                pass

        return AsyncContextManager()

    def get(self, endpoint, *args, response=None, **kwargs):
        return self._get_response(endpoint, response)

    def post(self, endpoint, *args, response=None, **kwargs):
        return self._get_response(endpoint, response)

    def request(self, *args, response=None, **kwargs):
        return self._get_response(response=response)

    async def close(self):
        self._closed = True
