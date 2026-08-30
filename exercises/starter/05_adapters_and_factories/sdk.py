"""Exercise 05: register storage adapters by URI scheme."""

from abc import ABC, abstractmethod
from typing import ClassVar
from urllib.parse import urlparse


class ArtifactStore(ABC):
    registry: ClassVar[dict[str, type["ArtifactStore"]]] = {}
    scheme: ClassVar[str]

    def __init_subclass__(cls, *, scheme: str | None = None, **kwargs: object) -> None:
        """Register concrete subclasses that declare a unique scheme."""
        raise NotImplementedError

    @abstractmethod
    def load(self, location: str) -> bytes: ...


class MemoryStore(ArtifactStore, scheme="mem"):
    values: ClassVar[dict[str, bytes]] = {}

    def load(self, location: str) -> bytes:
        raise NotImplementedError


def store_for(uri: str) -> ArtifactStore:
    """Build the adapter registered for uri's scheme; reject unknown schemes."""
    raise NotImplementedError

