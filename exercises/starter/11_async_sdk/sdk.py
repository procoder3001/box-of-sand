"""Exercise 11: an async client with bounded work, timeouts, and cleanup."""

import asyncio
from typing import Any, Protocol, Sequence


class AsyncTransport(Protocol):
    async def get(self, path: str) -> dict[str, Any]: ...
    async def aclose(self) -> None: ...


class SDKTimeoutError(Exception):
    pass


class AsyncModelsClient:
    def __init__(self, transport: AsyncTransport) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> "AsyncModelsClient":
        raise NotImplementedError

    async def __aexit__(self, *exc_info: object) -> None:
        """Close the transport even during failure or cancellation."""
        raise NotImplementedError

    async def get_many(
        self,
        names: Sequence[str],
        *,
        concurrency: int = 5,
        timeout: float = 10.0,
    ) -> list[dict[str, Any]]:
        """Fetch concurrently, bound active requests, and time out each request.

        Preserve input ordering. Reject non-positive concurrency and timeout.
        Translate asyncio.TimeoutError to SDKTimeoutError using exception chaining.
        Do not catch or translate asyncio.CancelledError.
        """
        raise NotImplementedError

