from io import StringIO

import company_mlops
from company_mlops.cli import run_cli
from company_mlops.client import MLOpsClient
from company_mlops.config import MLOpsConfig

from fakes import FakeMLflowBackend


def test_public_imports_are_intentional() -> None:
    assert company_mlops.__all__ == ["MLOpsClient", "MLOpsConfig", "Run"]


def test_cli_calls_same_service_used_by_library() -> None:
    backend = FakeMLflowBackend()
    client = MLOpsClient(MLOpsConfig("p", "r", "uri"), mlflow_backend=backend)
    stdout, stderr = StringIO(), StringIO()
    code = run_cli(
        ["experiment", "create", "fraud"],
        client=client,
        stdout=stdout,
        stderr=stderr,
    )
    assert code == 0
    assert stdout.getvalue() == "created experiment exp-1\n"
    assert stderr.getvalue() == ""
    assert backend.events == [("create_experiment", "fraud")]


def test_cli_translates_expected_input_error() -> None:
    client = MLOpsClient(MLOpsConfig("p", "r", "uri"), mlflow_backend=FakeMLflowBackend())
    stdout, stderr = StringIO(), StringIO()
    assert run_cli(
        ["experiment", "create", ""], client=client, stdout=stdout, stderr=stderr
    ) == 2
    assert "experiment name" in stderr.getvalue()

