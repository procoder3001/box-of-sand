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
        self._transport = transport

    def get(self, name: str) -> Model:
        data = self._transport.request("GET", f"/models/{name}")
        return Model(name=str(data["name"]), version=int(data["version"]))


class SDKClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport
        self._models: ModelsResource | None = None

    @property
    def models(self) -> ModelsResource:
        if self._models is None:
            self._models = ModelsResource(self._transport)
        return self._models

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "SDKClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

