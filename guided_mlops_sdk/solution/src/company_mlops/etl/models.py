from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class DatasetRef:
    uri: str

    def __post_init__(self) -> None:
        if not self.uri.strip():
            raise ValueError("dataset URI must not be empty")


class FeatureOperation(str, Enum):
    IDENTITY = "identity"
    RATIO = "ratio"


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    name: str
    operation: FeatureOperation
    inputs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("feature name must not be empty")
        expected = {FeatureOperation.IDENTITY: 1, FeatureOperation.RATIO: 2}
        if len(self.inputs) != expected[self.operation]:
            raise ValueError(
                f"{self.operation.value} requires {expected[self.operation]} input column(s)"
            )
        if any(not column.strip() for column in self.inputs):
            raise ValueError("feature input columns must not be empty")

    @classmethod
    def identity(cls, name: str, source_column: str) -> "FeatureSpec":
        return cls(name, FeatureOperation.IDENTITY, (source_column,))

    @classmethod
    def ratio(cls, name: str, numerator: str, denominator: str) -> "FeatureSpec":
        return cls(name, FeatureOperation.RATIO, (numerator, denominator))


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    provider: str
    job_id: str
    destination: DatasetRef

