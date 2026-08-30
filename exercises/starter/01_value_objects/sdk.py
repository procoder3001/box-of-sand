"""Exercise 01: implement validated SDK value objects."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """An immutable, hashable artifact identity."""

    bucket: str
    path: str

    @property
    def uri(self) -> str:
        """Return ``gs://<bucket>/<path>`` with no duplicate separator."""
        raise NotImplementedError


@dataclass(slots=True)
class ClientConfig:
    endpoint: str
    timeout: float = 10.0
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Reject a non-positive timeout and remove a trailing endpoint slash."""
        raise NotImplementedError

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "ClientConfig":
        """Construct from endpoint/timeout keys without retaining the mapping."""
        raise NotImplementedError

