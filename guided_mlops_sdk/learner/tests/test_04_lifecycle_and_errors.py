import pytest

from company_mlops.services.mlflow import MLflowService
from fakes import FakeMLflowBackend


def test_run_context_marks_success() -> None:
    backend = FakeMLflowBackend()
    with MLflowService(backend).run("exp-1", "training") as run:
        assert run.status == "RUNNING"
    assert backend.events == [
        ("start_run", "exp-1", "training"),
        ("end_run", "run-1", "FINISHED"),
    ]


def test_run_context_marks_failure_without_suppressing_it() -> None:
    backend = FakeMLflowBackend()
    with pytest.raises(RuntimeError, match="training failed"):
        with MLflowService(backend).run("exp-1", "training"):
            raise RuntimeError("training failed")
    assert backend.events[-1] == ("end_run", "run-1", "FAILED")

