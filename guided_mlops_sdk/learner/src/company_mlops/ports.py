"""Lesson 2: structural contracts for dependencies we do not own."""

from collections.abc import Mapping
from typing import Protocol


class MLflowBackend(Protocol):
    """The smallest backend capability used by this course SDK."""

    def create_experiment(self, name: str) -> str: ...
    def get_run(self, run_id: str) -> Mapping[str, object]: ...
    def start_run(self, experiment_id: str, name: str) -> str: ...
    def end_run(self, run_id: str, status: str) -> None: ...
    async def get_run_async(self, run_id: str) -> Mapping[str, object]: ...
    async def aclose(self) -> None: ...


class PipelineExecutor(Protocol):
    """A runtime-selectable strategy; inheritance is not required."""

    name: str

    def execute(self, pipeline: "PipelineSpec") -> str: ...


# Imported only for static checking, avoiding a runtime circular import.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipelines import PipelineSpec

