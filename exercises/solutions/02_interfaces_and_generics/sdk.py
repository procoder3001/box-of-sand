from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar, cast


class BlobStore(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes: ...

    @abstractmethod
    def write(self, key: str, value: bytes) -> None: ...


class Codec(Protocol):
    def encode(self, value: object) -> bytes: ...
    def decode(self, value: bytes) -> object: ...


T = TypeVar("T")


class Repository(Generic[T]):
    def __init__(self, store: BlobStore, codec: Codec) -> None:
        self._store = store
        self._codec = codec

    def save(self, key: str, value: T) -> None:
        self._store.write(key, self._codec.encode(value))

    def get(self, key: str) -> T:
        # This boundary trusts the injected codec to honor the repository's T.
        return cast(T, self._codec.decode(self._store.read(key)))


@dataclass
class MemoryBlobStore(BlobStore):
    values: dict[str, bytes]

    def read(self, key: str) -> bytes:
        return self.values[key]

    def write(self, key: str, value: bytes) -> None:
        self.values[key] = value

