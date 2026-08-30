import pytest

from company_mlops.client import MLOpsClient
from company_mlops.config import MLOpsConfig
from company_mlops.etl.executors import BeamExecutor, SparkExecutor
from company_mlops.etl.models import (
    DatasetRef,
    FeatureOperation,
    FeatureSpec,
    MaterializationResult,
)
from company_mlops.etl.plan import FeaturePlan, FeaturePlanBuilder

from fakes import FakeMLflowBackend


def build_plan() -> FeaturePlan:
    return (
        FeaturePlanBuilder(
            "training-features",
            source=DatasetRef("bq://project.raw.events"),
            destination=DatasetRef("bq://project.features.training"),
        )
        .add_feature(FeatureSpec.identity("country", "country_code"))
        .add_feature(FeatureSpec.ratio("click_rate", "clicks", "impressions"))
        .build()
    )


def test_feature_alternate_constructors_and_plan_validation() -> None:
    identity = FeatureSpec.identity("country", "country_code")
    assert identity.inputs == ("country_code",)
    with pytest.raises(ValueError, match="2 input"):
        FeatureSpec(identity.name, FeatureOperation.RATIO, ("clicks",))
    with pytest.raises(ValueError, match="duplicate"):
        (
            FeaturePlanBuilder(
                "features", source=DatasetRef("input"), destination=DatasetRef("output")
            )
            .add_feature(identity)
            .add_feature(identity)
        )


def test_spark_executor_compiles_portable_plan_for_spark_gateway() -> None:
    class FakeSparkGateway:
        def __init__(self) -> None:
            self.submission: dict[str, object] = {}

        def submit_sql_features(self, **submission: object) -> str:
            self.submission = submission
            return "spark-job-1"

    gateway = FakeSparkGateway()
    result = SparkExecutor(gateway).execute(build_plan())
    assert result.provider == "spark"
    assert result.job_id == "spark-job-1"
    assert gateway.submission["columns"] == {
        "country": "country_code",
        "click_rate": "(clicks / impressions)",
    }


def test_beam_executor_compiles_same_plan_to_different_boundary() -> None:
    class FakeBeamGateway:
        def __init__(self) -> None:
            self.transforms: object = None

        def submit_transforms(self, **submission: object) -> str:
            self.transforms = submission["transforms"]
            return "beam-job-1"

    gateway = FakeBeamGateway()
    result = BeamExecutor(gateway).execute(build_plan())
    assert result.provider == "beam"
    assert gateway.transforms == [
        {"output": "country", "operation": "identity", "inputs": ("country_code",)},
        {
            "output": "click_rate",
            "operation": "ratio",
            "inputs": ("clicks", "impressions"),
        },
    ]


def test_facade_exposes_same_etl_service_for_any_execution_strategy() -> None:
    client = MLOpsClient(
        MLOpsConfig("project", "region", "tracking"),
        mlflow_backend=FakeMLflowBackend(),
    )

    class RecordingExecutor:
        provider = "recording"

        def execute(self, plan: FeaturePlan) -> MaterializationResult:
            return MaterializationResult(self.provider, "job-1", plan.destination)

    plan = build_plan()
    assert client.etl is client.etl
    result = client.etl.materialize(plan, executor=RecordingExecutor())
    assert result == MaterializationResult("recording", "job-1", plan.destination)
