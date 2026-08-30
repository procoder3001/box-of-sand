from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from company_mlops.config import MLOpsConfig
from company_mlops.errors import ConfigurationError
from company_mlops.models import MLflowRunPayload, Run


def test_config_alternate_constructor_and_immutability() -> None:
    config = MLOpsConfig.from_env({
        "COMPANY_PROJECT": "ml-dev",
        "COMPANY_REGION": "us-central1",
        "MLFLOW_TRACKING_URI": "https://tracking.test",
    })
    assert config.project_id == "ml-dev"
    with pytest.raises(FrozenInstanceError):
        config.region = "changed"  # type: ignore[misc]


def test_missing_or_empty_config_has_package_error() -> None:
    with pytest.raises(ConfigurationError, match="COMPANY_REGION"):
        MLOpsConfig.from_env({"COMPANY_PROJECT": "p"})
    with pytest.raises(ConfigurationError, match="project_id"):
        MLOpsConfig("", "region", "uri")


def test_pydantic_validates_wire_data_but_dataclass_is_public_value() -> None:
    payload = MLflowRunPayload.model_validate({"run_id": "r1", "experiment_id": "e1"})
    run = Run(payload.run_id, payload.experiment_id, payload.status)
    assert run == Run("r1", "e1", "RUNNING")
    assert hash(run) == hash(Run("r1", "e1", "RUNNING"))
    with pytest.raises(ValidationError):
        MLflowRunPayload.model_validate({"run_id": "", "experiment_id": "e1", "extra": 1})

