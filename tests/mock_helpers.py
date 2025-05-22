import json
import os
from typing import Any
from typing import Optional

from surepy.client import SurePetcareClient


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
