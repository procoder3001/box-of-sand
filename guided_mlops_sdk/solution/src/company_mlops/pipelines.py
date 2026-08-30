from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar

from .ports import PipelineExecutor


@dataclass(frozen=True, slots=True)
class Step[OutputT]:
    name: str
    operation: Callable[[], OutputT]

    def run(self) -> OutputT:
        return self.operation()


@dataclass(frozen=True, slots=True)
class PipelineSpec:
    name: str
    steps: tuple[Step[object], ...]


class PipelineBuilder:
    def __init__(self, name: str) -> None:
        if not name.strip():
            raise ValueError("pipeline name must not be empty")
        self._name = name
        self._steps: list[Step[object]] = []

    def add_step[OutputT](self, step: Step[OutputT]) -> "PipelineBuilder":
        # Step is immutable and only run for side effects here; its concrete
        # OutputT need not be retained by PipelineSpec.
        self._steps.append(step)
        return self

    def build(self) -> PipelineSpec:
        if not self._steps:
            raise ValueError("a pipeline needs at least one step")
        return PipelineSpec(self._name, tuple(self._steps))


class LocalExecutor:
    name = "local"

    def execute(self, pipeline: PipelineSpec) -> str:
        for step in pipeline.steps:
            step.run()
        return f"local:{pipeline.name}"


class BaseCloudExecutor(ABC):
    provider: ClassVar[str]
    job_prefix: ClassVar[str] = "mlops"

    @classmethod
    def job_name(cls, pipeline: PipelineSpec) -> str:
        return f"{cls.job_prefix}-{cls.provider}-{pipeline.name}"

    def execute(self, pipeline: PipelineSpec) -> str:
        return self.submit(pipeline, job_name=self.job_name(pipeline))

    @abstractmethod
    def submit(self, pipeline: PipelineSpec, *, job_name: str) -> str: ...


class PipelinesService:
    def run(self, pipeline: PipelineSpec, *, executor: PipelineExecutor) -> str:
        return executor.execute(pipeline)
