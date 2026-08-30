from collections.abc import Mapping

from .config import MLOpsConfig
from .etl.service import ETLService
from .pipelines import PipelinesService
from .ports import MLflowBackend
from .services.mlflow import MLflowService


class MLOpsClient:
    sdk_name = "company-mlops"

    def __init__(self, config: MLOpsConfig, *, mlflow_backend: MLflowBackend) -> None:
        self.config = config
        self._mlflow_backend = mlflow_backend
        self._mlflow: MLflowService | None = None
        self._pipelines: PipelinesService | None = None
        self._etl: ETLService | None = None

    @classmethod
    def from_env(
        cls,
        *,
        mlflow_backend: MLflowBackend,
        environ: Mapping[str, str] | None = None,
    ) -> "MLOpsClient":
        return cls(MLOpsConfig.from_env(environ), mlflow_backend=mlflow_backend)

    @classmethod
    def user_agent(cls) -> str:
        return f"{cls.sdk_name}/0.1"

    @property
    def mlflow(self) -> MLflowService:
        if self._mlflow is None:
            self._mlflow = MLflowService(self._mlflow_backend)
        return self._mlflow

    @property
    def pipelines(self) -> PipelinesService:
        if self._pipelines is None:
            self._pipelines = PipelinesService()
        return self._pipelines

    @property
    def etl(self) -> ETLService:
        if self._etl is None:
            self._etl = ETLService()
        return self._etl
