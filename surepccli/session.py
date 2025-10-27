import os
from collections.abc import Mapping
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from dotenv import set_key
from dotenv import unset_key

from surepccli.const import Envs
from surepcio.client import SurePetcareClient


_session_manager: Optional["SessionManager"] = None
_env_loaded = False


def getEnvFile():
    return Path(os.path.expanduser(".surepccli.env"))


def load_env_once():
    global _env_loaded
    if not _env_loaded:
        load_dotenv(getEnvFile(), override=True)
        _env_loaded = True


def save_session(values: Mapping[str, str]):
    """
    Persist key/value pairs to the .env file.
    Accepts plain strings or Envs members as keys.
    """
    for key, value in values.items():
        if value is None:
            continue
        env_key = key.value if isinstance(key, Envs) else key
        set_key(getEnvFile(), env_key, value)


def clear_session():
    """Remove all known session keys from the .env file."""
    for key in Envs:
        unset_key(str(getEnvFile()), key)


def clear_env(key: Envs):
    """Remove a specific key from the .env file."""
    unset_key(str(getEnvFile()), key)


def get_session_manager() -> "SessionManager":
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def reset_session_manager():
    global _session_manager
    _session_manager = None


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
