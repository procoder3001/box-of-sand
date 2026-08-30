from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(*, attempts: int, retry_on: tuple[type[Exception], ...]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if attempts < 1:
        raise ValueError("attempts must be positive")

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(attempts):
                try:
                    return function(*args, **kwargs)
                except retry_on:
                    if attempt == attempts - 1:
                        raise
            raise AssertionError("unreachable")

        return wrapped

    return decorate

