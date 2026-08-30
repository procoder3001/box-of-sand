from collections.abc import Mapping, Sequence
from typing import Protocol

from .models import FeatureOperation, MaterializationResult
from .plan import FeaturePlan


class ETLExecutor(Protocol):
    provider: str

    def execute(self, plan: FeaturePlan) -> MaterializationResult: ...


class SparkGateway(Protocol):
    def submit_sql_features(
        self,
        *,
        source_uri: str,
        destination_uri: str,
        columns: Mapping[str, str],
    ) -> str: ...


class BeamGateway(Protocol):
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
        self._gateway = gateway

    def execute(self, plan: FeaturePlan) -> MaterializationResult:
        columns: dict[str, str] = {}
        for feature in plan.features:
            if feature.operation is FeatureOperation.IDENTITY:
                expression = feature.inputs[0]
            else:
                expression = f"({feature.inputs[0]} / {feature.inputs[1]})"
            columns[feature.name] = expression
        job_id = self._gateway.submit_sql_features(
            source_uri=plan.source.uri,
            destination_uri=plan.destination.uri,
            columns=columns,
        )
        return MaterializationResult(self.provider, job_id, plan.destination)


class BeamExecutor:
    provider = "beam"

    def __init__(self, gateway: BeamGateway) -> None:
        self._gateway = gateway

    def execute(self, plan: FeaturePlan) -> MaterializationResult:
        transforms = [
            {
                "output": feature.name,
                "operation": feature.operation.value,
                "inputs": feature.inputs,
            }
            for feature in plan.features
        ]
        job_id = self._gateway.submit_transforms(
            source_uri=plan.source.uri,
            destination_uri=plan.destination.uri,
            transforms=transforms,
        )
        return MaterializationResult(self.provider, job_id, plan.destination)

