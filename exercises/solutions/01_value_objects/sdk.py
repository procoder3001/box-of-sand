from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    bucket: str
    path: str

    @property
    def uri(self) -> str:
        return f"gs://{self.bucket}/{self.path.lstrip('/')}"


@dataclass(slots=True)
class ClientConfig:
    endpoint: str
    timeout: float = 10.0
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        self.endpoint = self.endpoint.rstrip("/")

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "ClientConfig":
        endpoint = str(values["endpoint"])
        timeout = float(values.get("timeout", 10.0))
        return cls(endpoint=endpoint, timeout=timeout)

