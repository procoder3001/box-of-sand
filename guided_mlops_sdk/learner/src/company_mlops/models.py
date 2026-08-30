"""Lesson 1: boundary models and internal values have different jobs."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field


class MLflowRunPayload(BaseModel):
    """Validate an untrusted MLflow-shaped response at the adapter boundary.

    Configure this model to reject unknown fields. Require non-empty identifiers.
    ``status`` defaults to ``RUNNING`` when absent.
    """

    model_config = ConfigDict(extra="forbid")
    run_id: str = Field(min_length=1)
    experiment_id: str = Field(min_length=1)
    status: str = "RUNNING"


@dataclass(frozen=True, slots=True)
class Run:
    """A small trusted value owned by our public API."""

    id: str
    experiment_id: str
    status: str

