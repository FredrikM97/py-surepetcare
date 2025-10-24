from collections.abc import Mapping
from typing import Optional

from dotenv import load_dotenv
from dotenv import set_key
from dotenv import unset_key

from surepccli.const import Envs
from surepccli.context import ENV_FILE
from surepccli.context import SessionManager


_session_manager: Optional[SessionManager] = None
_env_loaded = False


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def reset_session_manager():
    global _session_manager
    _session_manager = None


def load_env_once():
    global _env_loaded
    if not _env_loaded:
        load_dotenv(ENV_FILE, override=True)
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
        set_key(ENV_FILE, env_key, value)


def clear_session():
    """Remove all known session keys from the .env file."""
    for key in Envs:
        unset_key(str(ENV_FILE), key)


def clear_env(key: Envs):
    """Remove a specific key from the .env file."""
    unset_key(str(ENV_FILE), key)
