"""Lesson 2: translate third-party shapes at one boundary."""

from collections.abc import Mapping

from pydantic import ValidationError

from ..errors import RunNotFoundError, TrackingError
from ..models import MLflowRunPayload, Run


def adapt_run(raw: Mapping[str, object]) -> Run:
    """Validate a raw response, then return a package-owned Run.

    Implement with ``MLflowRunPayload.model_validate``. Translate Pydantic's
    ValidationError to TrackingError and preserve it as ``__cause__``.
    """
    raise NotImplementedError


class MLflowAdapter:
    """Wrap an MLflow-shaped client behind the SDK's backend contract.

    The wrapped object is intentionally untyped here: real third-party SDKs
    often expose large interfaces. This adapter is the one place that knows its
    method names and nested response shape.
    """

    def __init__(self, raw_client: object) -> None:
        raise NotImplementedError

    def get_run(self, run_id: str) -> Mapping[str, object]:
        """Flatten ``raw_client.get_run(run_id).info`` to a mapping.

        Translate a third-party KeyError to RunNotFoundError using chaining.
        """
        raise NotImplementedError

