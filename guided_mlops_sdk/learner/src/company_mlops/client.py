"""Lesson 3: the boring, obvious public facade."""

from collections.abc import Mapping

from .config import MLOpsConfig
from .etl.service import ETLService
from .pipelines import PipelinesService
from .ports import MLflowBackend
from .services.mlflow import MLflowService


class MLOpsClient:
    """Top-level facade; it wires resources but contains no domain logic."""

    sdk_name = "company-mlops"

    def __init__(self, config: MLOpsConfig, *, mlflow_backend: MLflowBackend) -> None:
        raise NotImplementedError

    @classmethod
    def from_env(
        cls,
        *,
        mlflow_backend: MLflowBackend,
        environ: Mapping[str, str] | None = None,
    ) -> "MLOpsClient":
        """Alternate constructor that delegates config creation to MLOpsConfig.

        Return ``cls(...)``, not ``MLOpsClient(...)``, so subclasses inherit a
        constructor that produces the subclass.
        """
        raise NotImplementedError

    @classmethod
    def user_agent(cls) -> str:
        """Read one class attribute for this class and all subclasses."""
        raise NotImplementedError

    @property
    def mlflow(self) -> MLflowService:
        """Lazily create and cache a resource using the injected backend."""
        raise NotImplementedError

    @property
    def pipelines(self) -> PipelinesService:
        raise NotImplementedError

    @property
    def etl(self) -> ETLService:
        """Lazily create the framework-neutral ETL resource."""
        raise NotImplementedError
