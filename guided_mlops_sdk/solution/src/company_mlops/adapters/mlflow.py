from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from ..errors import RunNotFoundError, TrackingError
from ..models import MLflowRunPayload, Run


def adapt_run(raw: Mapping[str, object]) -> Run:
    try:
        payload = MLflowRunPayload.model_validate(raw)
    except ValidationError as error:
        raise TrackingError("MLflow returned an invalid run") from error
    return Run(payload.run_id, payload.experiment_id, payload.status)


class MLflowAdapter:
    def __init__(self, raw_client: object) -> None:
        self._raw_client = raw_client

    def get_run(self, run_id: str) -> Mapping[str, object]:
        try:
            external_run = self._raw_client.get_run(run_id)  # type: ignore[attr-defined]
        except KeyError as error:
            raise RunNotFoundError(f"run {run_id!r} was not found") from error
        info: Any = external_run.info
        return {
            "run_id": info.run_id,
            "experiment_id": info.experiment_id,
            "status": info.status,
        }

