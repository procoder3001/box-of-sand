from abc import ABC, abstractmethod
from typing import ClassVar
from urllib.parse import urlparse


class ArtifactStore(ABC):
    registry: ClassVar[dict[str, type["ArtifactStore"]]] = {}
    scheme: ClassVar[str]

    def __init_subclass__(cls, *, scheme: str | None = None, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if scheme is None:
            return
        if scheme in cls.registry:
            raise ValueError(f"artifact scheme {scheme!r} already registered")
        cls.scheme = scheme
        cls.registry[scheme] = cls

    @abstractmethod
    def load(self, location: str) -> bytes: ...


class MemoryStore(ArtifactStore, scheme="mem"):
    values: ClassVar[dict[str, bytes]] = {}

    def load(self, location: str) -> bytes:
        return self.values[location]


def store_for(uri: str) -> ArtifactStore:
    scheme = urlparse(uri).scheme
    try:
        store_type = ArtifactStore.registry[scheme]
    except KeyError as error:
        raise ValueError(f"unknown artifact scheme: {scheme!r}") from error
    return store_type()

