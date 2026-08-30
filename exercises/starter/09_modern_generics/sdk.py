"""Exercise 09 (Python 3.12+): modern generic syntax for SDK pagination."""

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Protocol


class Identified(Protocol):
    id: str


type Decoder[T] = Callable[[Mapping[str, object]], T]


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    next_cursor: str | None = None


class Pager[T]:
    def __init__(
        self,
        fetch: Callable[[str | None], Mapping[str, object]],
        decode: Decoder[T],
    ) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """Lazily fetch pages and decode each raw item as T."""
        raise NotImplementedError


def index_by_id[T: Identified](items: Iterable[T]) -> dict[str, T]:
    """Retain each concrete item type while requiring an id attribute."""
    raise NotImplementedError

