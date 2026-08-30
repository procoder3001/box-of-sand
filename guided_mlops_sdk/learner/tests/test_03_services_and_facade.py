from company_mlops.client import MLOpsClient
from company_mlops.config import MLOpsConfig
from company_mlops.models import Run

from fakes import FakeMLflowBackend


def test_resources_are_lazy_cached_and_use_injected_backend() -> None:
    backend = FakeMLflowBackend()
    client = MLOpsClient(MLOpsConfig("p", "r", "uri"), mlflow_backend=backend)
    assert backend.events == []
    assert client.mlflow is client.mlflow
    assert client.mlflow.experiments is client.mlflow.experiments
    assert client.mlflow.experiments.create("fraud") == "exp-1"
    assert client.mlflow.get_run("r1") == Run("r1", "exp-1", "FINISHED")


def test_classmethods_support_subclasses_without_duplication() -> None:
    class TeamClient(MLOpsClient):
        sdk_name = "team-mlops"

    client = TeamClient.from_env(
        mlflow_backend=FakeMLflowBackend(),
        environ={
            "COMPANY_PROJECT": "p", "COMPANY_REGION": "r", "MLFLOW_TRACKING_URI": "uri"
        },
    )
    assert type(client) is TeamClient
    assert TeamClient.user_agent() == "team-mlops/0.1"

