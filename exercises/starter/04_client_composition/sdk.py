"""Exercise 04: build an explicit client from composable resources."""

from dataclasses import dataclass
from typing import Any, Protocol


class Transport(Protocol):
    def request(self, method: str, path: str, *, json: dict[str, object] | None = None) -> dict[str, Any]: ...
    def close(self) -> None: ...


@dataclass(frozen=True)
class Model:
    name: str
    version: int


class ModelsResource:
    def __init__(self, transport: Transport) -> None:
        raise NotImplementedError

    def get(self, name: str) -> Model:
        """GET /models/<name> and translate the response to Model."""
        raise NotImplementedError


class SDKClient:
    def __init__(self, transport: Transport) -> None:
        """Store the injected transport; do no I/O."""
        raise NotImplementedError

    @property
    def models(self) -> ModelsResource:
        """Lazily create and cache one ModelsResource."""
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> "SDKClient":
        raise NotImplementedError

    def __exit__(self, *exc_info: object) -> None:
        raise NotImplementedError

