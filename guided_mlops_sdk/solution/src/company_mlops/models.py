from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field


class MLflowRunPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str = Field(min_length=1)
    experiment_id: str = Field(min_length=1)
    status: str = "RUNNING"


@dataclass(frozen=True, slots=True)
class Run:
    id: str
    experiment_id: str
    status: str

