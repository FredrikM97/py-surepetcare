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
        method: str,
        endpoint: str = "",
        params: dict[str, Any] | None = None,
        parse: ParseFn | None = None,
        reuse: bool = True,
        household_id: int | None = None,
        chain: ChainFn | None = None,
    ) -> None:
        if not method.strip():
            raise InvalidCommandError("Command method must be a non-empty HTTP method string.")
        if parse is not None and chain is not None:
            raise InvalidCommandError(
                "Command cannot have both parse and chain. "
                "Use parse to extract data from a response, "
                "or chain to produce follow-up commands — not both."
            )
        if endpoint.endswith("/async"):
            if household_id is None:
                raise InvalidCommandError(
                    "Async write commands must include household_id for pending status polling. "
                    f"Method={method!r}, endpoint={endpoint!r}"
                )
        self.method: str = method
        self.endpoint: str = endpoint
        self.params: dict[str, Any] = params or {}
        self.parse: ParseFn | None = parse
        self.reuse: bool = reuse
        self.household_id: int | None = household_id
        self.chain: ChainFn | None = chain

    def __str__(self) -> str:
        return "Command(method={!r}, endpoint={!r}, params={!r})".format(
            self.method, self.endpoint, self.params
        )
