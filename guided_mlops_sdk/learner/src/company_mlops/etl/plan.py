"""Build and freeze a feature materialization plan."""

from dataclasses import dataclass

from .models import DatasetRef, FeatureSpec


@dataclass(frozen=True, slots=True)
class FeaturePlan:
    name: str
    source: DatasetRef
    destination: DatasetRef
    features: tuple[FeatureSpec, ...]


class FeaturePlanBuilder:
    """Mutable construction helper; completed plans remain immutable."""

    def __init__(self, name: str, *, source: DatasetRef, destination: DatasetRef) -> None:
        raise NotImplementedError

    def add_feature(self, feature: FeatureSpec) -> "FeaturePlanBuilder":
        """Reject duplicate output names and return self."""
        raise NotImplementedError

    def build(self) -> FeaturePlan:
        """Require at least one feature and snapshot the current feature list."""
        raise NotImplementedError

