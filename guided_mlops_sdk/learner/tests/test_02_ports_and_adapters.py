from dataclasses import dataclass

import pytest

from company_mlops.adapters.mlflow import MLflowAdapter, adapt_run
from company_mlops.errors import RunNotFoundError, TrackingError
from company_mlops.models import Run


def test_mapping_adapter_returns_package_model() -> None:
    assert adapt_run({"run_id": "r1", "experiment_id": "e1", "status": "FINISHED"}) == Run("r1", "e1", "FINISHED")
    with pytest.raises(TrackingError) as raised:
        adapt_run({"run_id": "r1"})
    assert raised.value.__cause__ is not None


def test_object_adapter_contains_third_party_shape() -> None:
    @dataclass
    class Info:
        run_id: str
        experiment_id: str
        status: str

    @dataclass
    class ExternalRun:
        info: Info

    class RawClient:
        def get_run(self, run_id: str) -> ExternalRun:
            return ExternalRun(Info(run_id, "e1", "RUNNING"))

    assert MLflowAdapter(RawClient()).get_run("r1") == {
        "run_id": "r1", "experiment_id": "e1", "status": "RUNNING"
    }


def test_adapter_translates_expected_vendor_error() -> None:
    class MissingClient:
        def get_run(self, run_id: str) -> object:
            raise KeyError(run_id)

    with pytest.raises(RunNotFoundError) as raised:
        MLflowAdapter(MissingClient()).get_run("missing")
    assert isinstance(raised.value.__cause__, KeyError)

