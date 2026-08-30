"""Lesson 7: a thin CLI adapter around the same library API."""

import argparse
from collections.abc import Sequence
from typing import TextIO

from .errors import MLOpsError
from .client import MLOpsClient


def run_cli(
    argv: Sequence[str],
    *,
    client: MLOpsClient,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    """Parse ``experiment create NAME`` and call ``client.mlflow``.

    Return 0 on success and 2 for expected SDK/user errors. Unexpected errors
    must propagate so programming defects are not disguised as friendly output.
    """
    raise NotImplementedError


def main() -> None:
    """Composition root for the console entry point.

    A real implementation would construct the third-party MLflow client and its
    adapter here. Leave this explicit TODO: importing the package must not create
    credentials, connect to services, or read configuration.
    """
    raise SystemExit("wire the production MLflow adapter in your real package")

