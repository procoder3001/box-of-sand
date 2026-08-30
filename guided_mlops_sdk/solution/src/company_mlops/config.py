import os
from collections.abc import Mapping
from dataclasses import dataclass

from .errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class MLOpsConfig:
    project_id: str
    region: str
    mlflow_uri: str

    def __post_init__(self) -> None:
        for name in ("project_id", "region", "mlflow_uri"):
            if not getattr(self, name).strip():
                raise ConfigurationError(f"{name} must not be empty")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "MLOpsConfig":
        values = os.environ if environ is None else environ
        try:
            return cls(
                project_id=values["COMPANY_PROJECT"],
                region=values["COMPANY_REGION"],
                mlflow_uri=values["MLFLOW_TRACKING_URI"],
            )
        except KeyError as error:
            raise ConfigurationError(f"missing environment variable: {error.args[0]}") from error

