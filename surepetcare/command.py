from typing import Any
from typing import Callable
from typing import Optional


class Command:
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
        return (
            f"Command(method={self.method!r}, endpoint={self.endpoint!r}, "
            f"params={self.params!r}, response_type={self.response_type!r})"
        )

    def __repr__(self) -> str:
        return self.__str__()
