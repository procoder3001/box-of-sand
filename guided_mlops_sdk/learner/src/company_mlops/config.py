"""Lesson 1: trusted, immutable SDK configuration."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MLOpsConfig:
    """A validated configuration snapshot used inside the SDK.

    Implement:
    - ``__post_init__``: project_id, region, and mlflow_uri must be non-empty.
    - ``from_env``: read COMPANY_PROJECT, COMPANY_REGION, and MLFLOW_TRACKING_URI.

    ``environ`` is injected so tests need not mutate the process environment.
    The default ``None`` means "read os.environ when called", avoiding a snapshot
    of environment variables at import time.
    """

    project_id: str
    region: str
    mlflow_uri: str

    def __post_init__(self) -> None:
        raise NotImplementedError

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "MLOpsConfig":
        raise NotImplementedError

