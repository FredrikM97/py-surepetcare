from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

if TYPE_CHECKING:
    from surepcio.devices.entities import SurePetcareResponse

from surepcio.security.exceptions import InvalidCommandError

type ParseFn = Callable[["SurePetcareResponse"], Any]
type ChainFn = Callable[["SurePetcareResponse"], "list[Command] | Command | None"]


class Command:
    """Represents a command to be sent to the Sure Petcare API."""

    def __init__(
        self,
        method: str | None = None,
        endpoint: str = "",
        params: dict[str, Any] | None = None,
        parse: ParseFn | None = None,
        reuse: bool = True,
        device: Any | None = None,
        chain: ChainFn | None = None,
    ) -> None:
        if parse is not None and chain is not None:
            raise InvalidCommandError(
                "Command cannot have both parse and chain. "
                "Use parse to extract data from a response, "
                "or chain to produce follow-up commands — not both."
            )
        self.method: str | None = method
        self.endpoint: str = endpoint
        self.params: dict[str, Any] = params or {}
        self.parse: ParseFn | None = parse
        self.reuse: bool = reuse
        self.device: Any | None = device
        self.chain: ChainFn | None = chain

    def __str__(self) -> str:
        return "Command(method={!r}, endpoint={!r}, params={!r})".format(
            self.method, self.endpoint, self.params
        )
