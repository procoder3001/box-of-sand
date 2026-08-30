import asyncio

import pytest

from company_mlops.errors import MLOpsTimeoutError
from company_mlops.services.mlflow import MLflowService
from fakes import FakeMLflowBackend


@pytest.mark.asyncio
async def test_async_reads_are_bounded_and_ordered() -> None:
    backend = FakeMLflowBackend(delay=0.01)
    runs = await MLflowService(backend).get_runs(["r1", "r2", "r3"], concurrency=2)
    assert [run.id for run in runs] == ["r1", "r2", "r3"]
    assert backend.max_active == 2


@pytest.mark.asyncio
async def test_timeout_is_translated_with_cause() -> None:
    backend = FakeMLflowBackend(delay=1)
    with pytest.raises(MLOpsTimeoutError) as raised:
        await MLflowService(backend).get_runs(["slow"], timeout=0.001)
    assert isinstance(raised.value.__cause__, TimeoutError)


@pytest.mark.asyncio
async def test_cancellation_is_not_translated() -> None:
    backend = FakeMLflowBackend(delay=10)
    task = asyncio.create_task(MLflowService(backend).get_runs(["r1", "r2"], concurrency=2))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert backend.active == 0

