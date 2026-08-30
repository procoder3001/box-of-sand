import asyncio
from typing import Any, Protocol, Sequence


class AsyncTransport(Protocol):
    async def get(self, path: str) -> dict[str, Any]: ...
    async def aclose(self) -> None: ...


class SDKTimeoutError(Exception):
    pass


class AsyncModelsClient:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def __aenter__(self) -> "AsyncModelsClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self._transport.aclose()

    async def get_many(
        self,
        names: Sequence[str],
        *,
        concurrency: int = 5,
        timeout: float = 10.0,
    ) -> list[dict[str, Any]]:
        if concurrency < 1:
            raise ValueError("concurrency must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        semaphore = asyncio.Semaphore(concurrency)

        async def fetch(name: str) -> dict[str, Any]:
            async with semaphore:
                try:
                    return await asyncio.wait_for(
                        self._transport.get(f"/models/{name}"),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError as error:
                    raise SDKTimeoutError(f"timed out fetching model {name!r}") from error

        return list(await asyncio.gather(*(fetch(name) for name in names)))

