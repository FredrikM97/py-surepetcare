from typing import Any
from typing import Callable
from typing import Optional


class Command:
    """Represents a command to be sent to the Sure Petcare API."""
    def __init__(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[Any, Any]] = None,
        response_type: Optional[str] = None,
        callback: Optional[Callable] = None,
        reuse: bool = True,
    ):
        self.method = method
        self.endpoint = endpoint
        self.params = params or {}
        self.response_type = response_type
        self.callback = callback
        self.reuse = reuse

    def __str__(self) -> str:
        return "Command(method={!r}, endpoint={!r}, params={!r}, response_type={!r})".format(
            self.method, self.endpoint, self.params, self.response_type
        )

    def __repr__(self) -> str:
        return self.__str__()
