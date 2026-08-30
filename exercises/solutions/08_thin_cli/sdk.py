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
        if not model.strip():
            raise DeploymentError("model must not be empty")
        if replicas < 1:
            raise DeploymentError("replicas must be positive")
        return self.gateway.create(model, replicas)


def run_cli(argv: Sequence[str], service: DeploymentService, stdout: TextIO, stderr: TextIO) -> int:
    try:
        if len(argv) != 4 or argv[0] != "deploy" or argv[2] != "--replicas":
            raise DeploymentError("usage: deploy MODEL --replicas N")
        try:
            replicas = int(argv[3])
        except ValueError as error:
            raise DeploymentError("replicas must be an integer") from error
        deployment_id = service.deploy(argv[1], replicas)
    except DeploymentError as error:
        print(f"error: {error}", file=stderr)
        return 2
    print(f"deployed {deployment_id}", file=stdout)
    return 0

