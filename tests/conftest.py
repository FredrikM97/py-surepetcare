import enum
import json
from pathlib import Path
from unittest.mock import ANY
from urllib.parse import urlparse

import aresponses
import pytest
from syrupy.assertion import SnapshotAssertion

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


def register_device_api_mocks(aresponses: aresponses.ResponsesMockServer, mock_devices: list[dict]):
    for method_dict in mock_devices:
        for method, device in method_dict.items():
            for url, payload in device.items():
                parsed = urlparse(url)
                host = parsed.netloc
                path = parsed.path
                if parsed.query:
                    path += "?" + parsed.query

                aresponses.add(
                    host,
                    path,
                    method,
                    aresponses.Response(
                        body=json.dumps(payload),
                        status=200,
                        headers={"Content-Type": "application/json"},
                    ),
                    match_querystring=True,
                )


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
        return {k: serialize(v) for k, v in vars(obj).items() if not k.startswith("_")}
    else:
        return obj


def object_snapshot(data, snapshot: SnapshotAssertion, skip_fields=None, any_fields=None):
    data = mask_fields(
        data,
        skip_fields=skip_fields,
        any_fields=any_fields,
    )
    assert serialize(data) == snapshot
