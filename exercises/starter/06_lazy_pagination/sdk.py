"""Exercise 06: expose transport pagination as a lazy iterator."""

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
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        """Fetch the first page only when iteration begins, then follow cursors."""
        raise NotImplementedError

