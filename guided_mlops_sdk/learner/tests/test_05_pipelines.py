import pytest

from company_mlops.pipelines import (
    BaseCloudExecutor,
    LocalExecutor,
    PipelineBuilder,
    PipelinesService,
    Step,
)


def test_builder_snapshots_steps_and_strategy_executes_them() -> None:
    events: list[str] = []
    builder = PipelineBuilder("training").add_step(Step("extract", lambda: events.append("extract")))
    first = builder.build()
    builder.add_step(Step("train", lambda: events.append("train")))
    assert [step.name for step in first.steps] == ["extract"]
    assert PipelinesService().run(first, executor=LocalExecutor()) == "local:training"
    assert events == ["extract"]


def test_builder_rejects_invalid_incomplete_specs() -> None:
    with pytest.raises(ValueError, match="name"):
        PipelineBuilder("")
    with pytest.raises(ValueError, match="step"):
        PipelineBuilder("empty").build()


def test_protocol_strategy_needs_no_inheritance() -> None:
    class RecordingExecutor:
        name = "recording"

        def execute(self, pipeline: object) -> str:
            return "job-42"

    pipeline = PipelineBuilder("p").add_step(Step("noop", lambda: None)).build()
    assert PipelinesService().run(pipeline, executor=RecordingExecutor()) == "job-42"


def test_abc_shares_policy_and_requires_only_provider_submission() -> None:
    class VertexExecutor(BaseCloudExecutor):
        provider = "vertex"

        def submit(self, pipeline: object, *, job_name: str) -> str:
            return f"submitted:{job_name}"

    pipeline = PipelineBuilder("training").add_step(Step("noop", lambda: None)).build()
    assert VertexExecutor.job_name(pipeline) == "mlops-vertex-training"
    assert VertexExecutor().execute(pipeline) == "submitted:mlops-vertex-training"

    class TeamVertexExecutor(VertexExecutor):
        job_prefix = "risk"

    assert TeamVertexExecutor.job_name(pipeline) == "risk-vertex-training"
