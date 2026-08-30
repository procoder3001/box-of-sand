"""Lessons 3, 4, and 6: service resources and lifecycles."""

import asyncio
from collections.abc import Sequence
from types import TracebackType

from ..errors import MLOpsTimeoutError
from ..models import Run
from ..ports import MLflowBackend
from ..adapters.mlflow import adapt_run


class ExperimentsResource:
    def __init__(self, backend: MLflowBackend) -> None:
        raise NotImplementedError

    def create(self, name: str) -> str:
        """Validate a non-empty name, then delegate to the backend."""
        raise NotImplementedError


class ManagedRun:
    """Context manager that owns exactly one tracking-run lifecycle."""

    def __init__(self, backend: MLflowBackend, experiment_id: str, name: str) -> None:
        raise NotImplementedError

    def __enter__(self) -> Run:
        """Start the run and return a package-owned RUNNING value."""
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """End FINISHED on success and FAILED on error; never suppress errors."""
        raise NotImplementedError


class MLflowService:
    def __init__(self, backend: MLflowBackend) -> None:
        raise NotImplementedError

    @property
    def experiments(self) -> ExperimentsResource:
        """Lazily create and cache the nested resource."""
        raise NotImplementedError

    def get_run(self, run_id: str) -> Run:
        raise NotImplementedError

    def run(self, experiment_id: str, name: str) -> ManagedRun:
        """Return a context manager; do not start work until ``with`` begins."""
        raise NotImplementedError

    async def get_runs(
        self,
        run_ids: Sequence[str],
        *,
        concurrency: int = 5,
        timeout: float = 10.0,
    ) -> list[Run]:
        """Fetch runs concurrently, bounded by a semaphore.

        Preserve input order. Apply a timeout to each request, translate timeout
        errors with chaining, and allow CancelledError to propagate unchanged.
        """
        raise NotImplementedError

