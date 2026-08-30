"""Exercise 03: write a signature-preserving retry decorator."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(*, attempts: int, retry_on: tuple[type[Exception], ...]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry matching failures at most ``attempts`` total times.

    Validate attempts when the decorator is created. Re-raise the last error.
    """
    raise NotImplementedError

