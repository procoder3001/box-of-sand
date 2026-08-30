"""Provider-specific compilation belongs behind executor adapters."""

from collections.abc import Mapping, Sequence
from typing import Protocol

from .models import MaterializationResult
from .plan import FeaturePlan


class ETLExecutor(Protocol):
    """Strategy selected by the caller; implementations need not inherit."""

    provider: str

    def execute(self, plan: FeaturePlan) -> MaterializationResult: ...


class SparkGateway(Protocol):
    """Narrow boundary a real adapter can implement using SparkSession."""

    def submit_sql_features(
        self,
        *,
        source_uri: str,
        destination_uri: str,
        columns: Mapping[str, str],
    ) -> str: ...


class BeamGateway(Protocol):
    """Narrow boundary a real adapter can implement using a Beam runner."""

    def submit_transforms(
        self,
        *,
        source_uri: str,
        destination_uri: str,
        transforms: Sequence[Mapping[str, object]],
    ) -> str: ...


class SparkExecutor:
    provider = "spark"

    def __init__(self, gateway: SparkGateway) -> None:
        raise NotImplementedError

    def execute(self, plan: FeaturePlan) -> MaterializationResult:
        """Compile portable features to SQL-shaped expressions and submit."""
        raise NotImplementedError


class BeamExecutor:
    provider = "beam"

    def __init__(self, gateway: BeamGateway) -> None:
        raise NotImplementedError

    def execute(self, plan: FeaturePlan) -> MaterializationResult:
        """Compile portable features to transform descriptions and submit."""
        raise NotImplementedError

