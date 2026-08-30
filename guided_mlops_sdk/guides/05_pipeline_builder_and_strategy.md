# Lesson 5: pipeline specs, modern generics, builder, and strategy

## Why these patterns belong together

A pipeline definition is immutable data. Constructing it may be ordered and compositional. Executing it is behavior that varies by environment. Those are three different responsibilities:

- `PipelineSpec`: frozen dataclass value.
- `PipelineBuilder`: temporary mutable construction helper.
- `PipelineExecutor`: injected behavioral strategy.

## Files to edit

1. Open `pipelines.py` and inspect the Python 3.12 syntax.
2. Implement `Step.run`.
3. Implement `PipelineBuilder`.
4. Implement `LocalExecutor`, `BaseCloudExecutor`, and `PipelinesService.run`.
5. Run `pytest -q tests/test_05_pipelines.py`.

## Modern generic syntax

```python
class Step[OutputT]:
    operation: Callable[[], OutputT]

    def run(self) -> OutputT: ...
```

`OutputT` is valuable because it links the callable's output to `run()`'s output. Without that relationship, a generic adds ceremony but no useful information.

The generic method:

```python
def add_step[OutputT](self, step: Step[OutputT]) -> PipelineBuilder:
    ...
```

accepts steps producing different concrete types. The completed `PipelineSpec` intentionally erases those individual output types because this small executor runs steps only for their effects. A richer DAG might preserve typed connections between step outputs and inputs, but that would be overengineering here.

## Why a builder here—but not everywhere?

The builder accumulates an ordered collection and validates completeness at `build()`. It snapshots the mutable list into a tuple so later builder changes cannot mutate an existing spec.

For four independent config fields, use a dataclass with keyword arguments. Do not create `ExperimentBuilder`, `BucketBuilder`, and `ClientBuilder` just to imitate other SDKs.

## Why a protocol strategy?

Local and Vertex execution vary at runtime but satisfy the same capability. An injected protocol avoids repeated `if backend == ...` branches and permits a test strategy without inheritance.

An ABC is justified when executors intentionally reuse a substantial base
algorithm or join an SDK-owned contract. The lesson includes that contrasting
case in `BaseCloudExecutor`.
Cloud executors intentionally join an SDK-owned family, reuse the concrete
`execute` template, and implement only `submit`. Its `job_name` classmethod reads
`cls.job_prefix` and `cls.provider`, so a subclass changes metadata once without
copying the naming algorithm. That is a justified ABC plus classmethod; the
lightweight `RecordingExecutor` test remains a justified protocol strategy.

## Hints

- The builder owns a `list`; `PipelineSpec` receives `tuple(self._steps)`.
- Return `self` from `add_step`.
- `LocalExecutor` loops through steps in their declared order.
- `PipelinesService` should be a one-line delegation.
- `BaseCloudExecutor.execute` calls `self.submit(..., job_name=self.job_name(...))`.

## Apply this to your SDK

Start with immutable pipeline specs and injected executors. Add a builder only if real configurations become multi-stage. Keep provider submission logic inside executor adapters, not inside the spec.

## Check your understanding

- What relationship does `OutputT` preserve?
- Why is `PipelineSpec.steps` a tuple?
- At what point would a simple `execute_pipeline(spec, executor)` function be enough?
