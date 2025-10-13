import os
from pathlib import Path

from surepccli.const import Envs
from surepcio.client import SurePetcareClient

ENV_FILE = Path(os.path.expanduser(".surepccli.env"))


class SessionManager:
    """Session manager using .env file for credentials."""

    def __init__(self):
        token = os.getenv(Envs.TOKEN)
        client_id = os.getenv(Envs.CLIENT_ID)
        self.client = SurePetcareClient()
        if token and client_id:
            self.client._token = token
            self.client._device_id = client_id

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def aclose(self):
        if self.client:
            await self.client.close()

    async def close(self):
        if self.client:
            await self.client.close()
