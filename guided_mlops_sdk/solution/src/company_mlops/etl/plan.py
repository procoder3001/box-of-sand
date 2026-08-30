from dataclasses import dataclass

from .models import DatasetRef, FeatureSpec


@dataclass(frozen=True, slots=True)
class FeaturePlan:
    name: str
    source: DatasetRef
    destination: DatasetRef
    features: tuple[FeatureSpec, ...]


class FeaturePlanBuilder:
    def __init__(self, name: str, *, source: DatasetRef, destination: DatasetRef) -> None:
        if not name.strip():
            raise ValueError("feature plan name must not be empty")
        self._name = name
        self._source = source
        self._destination = destination
        self._features: list[FeatureSpec] = []

    def add_feature(self, feature: FeatureSpec) -> "FeaturePlanBuilder":
        if any(existing.name == feature.name for existing in self._features):
            raise ValueError(f"duplicate feature name: {feature.name!r}")
        self._features.append(feature)
        return self

    def build(self) -> FeaturePlan:
        if not self._features:
            raise ValueError("a feature plan requires at least one feature")
        return FeaturePlan(
            self._name,
            self._source,
            self._destination,
            tuple(self._features),
        )

