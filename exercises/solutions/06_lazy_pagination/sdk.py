from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    next_cursor: str | None


class ModelPager:
    def __init__(self, fetch_page: Callable[[str | None], Page[str]]) -> None:
        self._fetch_page = fetch_page

    def __iter__(self) -> Iterator[str]:
        cursor: str | None = None
        while True:
            page = self._fetch_page(cursor)
            yield from page.items
            if page.next_cursor is None:
                return
            cursor = page.next_cursor

