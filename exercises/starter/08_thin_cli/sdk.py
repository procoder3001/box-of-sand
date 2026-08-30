"""Exercise 08: keep command parsing separate from the library service."""

from dataclasses import dataclass
from typing import Protocol, Sequence, TextIO


class DeploymentError(Exception):
    pass


class DeploymentGateway(Protocol):
    def create(self, model: str, replicas: int) -> str: ...


@dataclass
class DeploymentService:
    gateway: DeploymentGateway

    def deploy(self, model: str, replicas: int) -> str:
        """Validate domain inputs, then call the gateway."""
        raise NotImplementedError


def run_cli(argv: Sequence[str], service: DeploymentService, stdout: TextIO, stderr: TextIO) -> int:
    """Parse ``deploy MODEL --replicas N`` and translate errors to exit codes.

    Return 0 on success and 2 for usage/domain errors. Do not construct the
    service or gateway here; callers inject them.
    """
    raise NotImplementedError

