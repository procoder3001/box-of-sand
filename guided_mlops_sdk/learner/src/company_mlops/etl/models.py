"""Immutable, framework-neutral ETL and feature-engineering values."""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class DatasetRef:
    """A logical dataset location understood by execution adapters."""

    uri: str

    def __post_init__(self) -> None:
        """Require a non-empty URI."""
        raise NotImplementedError


class FeatureOperation(str, Enum):
    """The deliberately tiny portable feature vocabulary in this course."""

    IDENTITY = "identity"
    RATIO = "ratio"


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    """A declarative feature that Spark and Beam adapters can compile.

    IDENTITY requires one input column. RATIO requires numerator and
    denominator columns in that order. Validate those arities in __post_init__.
    """

    name: str
    operation: FeatureOperation
    inputs: tuple[str, ...]

    def __post_init__(self) -> None:
        raise NotImplementedError

    @classmethod
    def identity(cls, name: str, source_column: str) -> "FeatureSpec":
        """Named alternate constructor for the common one-column feature."""
        raise NotImplementedError

    @classmethod
    def ratio(cls, name: str, numerator: str, denominator: str) -> "FeatureSpec":
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    provider: str
    job_id: str
    destination: DatasetRef

