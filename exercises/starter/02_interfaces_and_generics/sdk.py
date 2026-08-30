"""Exercise 02: combine an ABC, a protocol, and a generic repository."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar


class BlobStore(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes:
        """Read raw bytes or raise KeyError."""

    @abstractmethod
    def write(self, key: str, value: bytes) -> None:
        """Write raw bytes."""


class Codec(Protocol):
    def encode(self, value: object) -> bytes: ...
    def decode(self, value: bytes) -> object: ...


T = TypeVar("T")


class Repository(Generic[T]):
    def __init__(self, store: BlobStore, codec: Codec) -> None:
        raise NotImplementedError

    def save(self, key: str, value: T) -> None:
        raise NotImplementedError

    def get(self, key: str) -> T:
        raise NotImplementedError


@dataclass
class MemoryBlobStore(BlobStore):
    values: dict[str, bytes]

    def read(self, key: str) -> bytes:
        raise NotImplementedError

    def write(self, key: str, value: bytes) -> None:
        raise NotImplementedError

