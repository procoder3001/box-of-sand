from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class ModelPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    version: int = Field(ge=1)


@dataclass(frozen=True, slots=True)
class ModelRef:
    name: str
    version: int


class Transport(Protocol):
    def get(self, path: str) -> dict[str, Any]: ...


class ArtifactStore(ABC):
    def model_key(self, model: ModelRef) -> str:
        return f"{model.name}/{model.version}/model.bin"

    @abstractmethod
    def save(self, key: str, content: bytes) -> None: ...


class ModelsClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def get(self, name: str) -> ModelRef:
        payload = ModelPayload.model_validate(self._transport.get(f"/models/{name}"))
        return ModelRef(name=payload.name, version=payload.version)


class ModelArchiver:
    def __init__(self, store: ArtifactStore) -> None:
        self._store = store

    def archive(self, model: ModelRef, content: bytes) -> str:
        key = self._store.model_key(model)
        self._store.save(key, content)
        return key

