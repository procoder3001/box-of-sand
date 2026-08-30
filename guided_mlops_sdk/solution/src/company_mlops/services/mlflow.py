import asyncio
from collections.abc import Sequence
from types import TracebackType

from ..adapters.mlflow import adapt_run
from ..errors import MLOpsTimeoutError
from ..models import Run
from ..ports import MLflowBackend


class ExperimentsResource:
    def __init__(self, backend: MLflowBackend) -> None:
        self._backend = backend

    def create(self, name: str) -> str:
        if not name.strip():
            raise ValueError("experiment name must not be empty")
        return self._backend.create_experiment(name)


class ManagedRun:
    def __init__(self, backend: MLflowBackend, experiment_id: str, name: str) -> None:
        self._backend = backend
        self._experiment_id = experiment_id
        self._name = name
        self._run_id: str | None = None

    def __enter__(self) -> Run:
        self._run_id = self._backend.start_run(self._experiment_id, self._name)
        return Run(self._run_id, self._experiment_id, "RUNNING")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._run_id is None:
            return
        status = "FINISHED" if exc_type is None else "FAILED"
        self._backend.end_run(self._run_id, status)


class MLflowService:
    def __init__(self, backend: MLflowBackend) -> None:
        self._backend = backend
        self._experiments: ExperimentsResource | None = None

    @property
    def experiments(self) -> ExperimentsResource:
        if self._experiments is None:
            self._experiments = ExperimentsResource(self._backend)
        return self._experiments

    def get_run(self, run_id: str) -> Run:
        return adapt_run(self._backend.get_run(run_id))

    def run(self, experiment_id: str, name: str) -> ManagedRun:
        return ManagedRun(self._backend, experiment_id, name)

    async def get_runs(
        self,
        run_ids: Sequence[str],
        *,
        concurrency: int = 5,
        timeout: float = 10.0,
    ) -> list[Run]:
        if concurrency < 1:
            raise ValueError("concurrency must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        semaphore = asyncio.Semaphore(concurrency)

        async def get_one(run_id: str) -> Run:
            async with semaphore:
                try:
                    raw = await asyncio.wait_for(
                        self._backend.get_run_async(run_id), timeout=timeout
                    )
                except TimeoutError as error:
                    raise MLOpsTimeoutError(f"timed out fetching run {run_id!r}") from error
                return adapt_run(raw)

        return list(await asyncio.gather(*(get_one(run_id) for run_id in run_ids)))

