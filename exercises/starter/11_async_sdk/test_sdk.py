import asyncio
import unittest

from sdk import AsyncModelsClient, SDKTimeoutError


class FakeAsyncTransport:
    def __init__(self, delay: float = 0.01) -> None:
        self.delay = delay
        self.active = 0
        self.max_active = 0
        self.closed = False
        self.cancelled = 0

    async def get(self, path: str) -> dict[str, object]:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(self.delay)
            return {"name": path.rsplit("/", 1)[-1]}
        except asyncio.CancelledError:
            self.cancelled += 1
            raise
        finally:
            self.active -= 1

    async def aclose(self) -> None:
        self.closed = True


class AsyncClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_bounds_concurrency_and_preserves_order(self) -> None:
        transport = FakeAsyncTransport()
        async with AsyncModelsClient(transport) as client:
            models = await client.get_many(["a", "b", "c", "d"], concurrency=2)
        self.assertEqual([model["name"] for model in models], ["a", "b", "c", "d"])
        self.assertEqual(transport.max_active, 2)
        self.assertTrue(transport.closed)

    async def test_timeout_is_translated_and_transport_closes(self) -> None:
        transport = FakeAsyncTransport(delay=0.1)
        with self.assertRaises(SDKTimeoutError) as raised:
            async with AsyncModelsClient(transport) as client:
                await client.get_many(["slow"], timeout=0.001)
        self.assertIsInstance(raised.exception.__cause__, TimeoutError)
        self.assertTrue(transport.closed)

    async def test_cancellation_propagates_and_still_closes(self) -> None:
        transport = FakeAsyncTransport(delay=10)
        started = asyncio.Event()

        async def operation() -> None:
            async with AsyncModelsClient(transport) as client:
                started.set()
                await client.get_many(["a", "b"], concurrency=2)

        task = asyncio.create_task(operation())
        await started.wait()
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(transport.closed)
        self.assertEqual(transport.active, 0)

    async def test_rejects_invalid_limits_before_starting_work(self) -> None:
        client = AsyncModelsClient(FakeAsyncTransport())
        with self.assertRaises(ValueError):
            await client.get_many(["a"], concurrency=0)
        with self.assertRaises(ValueError):
            await client.get_many(["a"], timeout=0)


if __name__ == "__main__":
    unittest.main()

