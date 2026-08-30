"""Python 3.12+ reference solution using PEP 695 syntax."""

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Protocol, cast


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
        self._fetch = fetch
        self._decode = decode

    def __iter__(self) -> Iterator[T]:
        cursor: str | None = None
        while True:
            raw_page = self._fetch(cursor)
            raw_items = cast(list[Mapping[str, object]], raw_page["items"])
            yield from (self._decode(item) for item in raw_items)
            next_cursor = raw_page.get("next_cursor")
            if next_cursor is None:
                return
            cursor = str(next_cursor)


def index_by_id[T: Identified](items: Iterable[T]) -> dict[str, T]:
    return {item.id: item for item in items}

