"""Lesson 5: immutable specs, a bounded generic, strategy, and builder."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar

from .ports import PipelineExecutor


@dataclass(frozen=True, slots=True)
class Step[OutputT]:
    """A Python 3.12 generic preserving the callable/result relationship."""

    name: str
    operation: Callable[[], OutputT]

    def run(self) -> OutputT:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class PipelineSpec:
    name: str
    steps: tuple[Step[object], ...]


class PipelineBuilder:
    """Use a builder because pipeline construction is ordered and compositional."""

    def __init__(self, name: str) -> None:
        raise NotImplementedError

    def add_step[OutputT](self, step: Step[OutputT]) -> "PipelineBuilder":
        """Append and return self for fluent construction."""
        raise NotImplementedError

    def build(self) -> PipelineSpec:
        """Require at least one step and snapshot mutable builder state."""
        raise NotImplementedError


class LocalExecutor:
    """Simple strategy for local execution; no base class is necessary."""

    name = "local"

    def execute(self, pipeline: PipelineSpec) -> str:
        """Run steps in order and return ``local:<pipeline-name>``."""
        raise NotImplementedError


class BaseCloudExecutor(ABC):
    """SDK-owned family sharing job naming while delegating submission.

    This is an ABC—not merely a Protocol—because subclasses intentionally join
    our inheritance family and reuse the concrete ``execute`` algorithm.
    """

    provider: ClassVar[str]
    job_prefix: ClassVar[str] = "mlops"

    @classmethod
    def job_name(cls, pipeline: PipelineSpec) -> str:
        """Build one name policy from attributes subclasses may override."""
        raise NotImplementedError

    def execute(self, pipeline: PipelineSpec) -> str:
        """Shared template method that delegates the variable provider step."""
        raise NotImplementedError

    @abstractmethod
    def submit(self, pipeline: PipelineSpec, *, job_name: str) -> str:
        """Submit through one provider and return its job identifier."""


class PipelinesService:
    def run(self, pipeline: PipelineSpec, *, executor: PipelineExecutor) -> str:
        raise NotImplementedError
