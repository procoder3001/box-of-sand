import argparse
import sys
from collections.abc import Sequence
from typing import TextIO

from .client import MLOpsClient
from .errors import MLOpsError


def run_cli(
    argv: Sequence[str],
    *,
    client: MLOpsClient,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    parser = argparse.ArgumentParser(prog="company-mlops", exit_on_error=False)
    commands = parser.add_subparsers(dest="resource", required=True)
    experiment = commands.add_parser("experiment", exit_on_error=False)
    actions = experiment.add_subparsers(dest="action", required=True)
    create = actions.add_parser("create", exit_on_error=False)
    create.add_argument("name")
    try:
        arguments = parser.parse_args(list(argv))
        experiment_id = client.mlflow.experiments.create(arguments.name)
    except (argparse.ArgumentError, MLOpsError, ValueError) as error:
        print(f"error: {error}", file=stderr)
        return 2
    print(f"created experiment {experiment_id}", file=stdout)
    return 0


def main() -> None:
    raise SystemExit("wire the production MLflow adapter in your real package")

