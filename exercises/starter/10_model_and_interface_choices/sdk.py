"""Exercise 10: put validation, values, interfaces, and behavior in the right types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class ModelPayload(BaseModel):
    """Untrusted response at the external boundary: validate it strictly."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    version: int = Field(ge=1)


@dataclass(frozen=True, slots=True)
class ModelRef:
    """Small trusted internal value after boundary validation."""

    name: str
    version: int


class Transport(Protocol):
    """Injected capability: implementations do not need to inherit."""

    def get(self, path: str) -> dict[str, Any]: ...


class ArtifactStore(ABC):
    """SDK-owned extension family with a shared helper and required operation."""

    def model_key(self, model: ModelRef) -> str:
        return f"{model.name}/{model.version}/model.bin"

    @abstractmethod
    def save(self, key: str, content: bytes) -> None: ...


class ModelsClient:
    def __init__(self, transport: Transport) -> None:
        raise NotImplementedError

    def get(self, name: str) -> ModelRef:
        """Validate transport data with Pydantic, then return a dataclass value."""
        raise NotImplementedError


class ModelArchiver:
    def __init__(self, store: ArtifactStore) -> None:
        raise NotImplementedError

    def archive(self, model: ModelRef, content: bytes) -> str:
        """Use the ABC's shared key policy and concrete save implementation."""
        raise NotImplementedError

