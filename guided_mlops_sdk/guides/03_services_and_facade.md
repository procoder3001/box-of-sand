# Lesson 3: services, resources, and the public facade

## The user experience

The public API should be unsurprising:

```python
client.mlflow.experiments.create("fraud")
client.mlflow.get_run("run-1")
client.pipelines.run(spec, executor=executor)
```

Users should not construct internal managers. The facade groups capabilities; services implement use cases; adapters isolate external APIs.

## Files to edit

1. Implement `ExperimentsResource` and the synchronous methods of `MLflowService` in `services/mlflow.py`.
2. Implement all TODOs in `client.py`.
3. Run `pytest -q tests/test_03_services_and_facade.py`.

Leave `ManagedRun` and `get_runs` for later lessons.

## Step-by-step design

Store the backend in each service. `ExperimentsResource.create` performs package/domain validation, then delegates. It does not know how authentication or HTTP works.

Lazily create nested resources in properties and cache them. Construction stays free of I/O either way, but laziness avoids eagerly building a large object graph. A direct eager attribute would also be fine for a tiny package; this lesson mirrors common SDK ergonomics.

In `MLOpsClient`, save the configuration and backend. Initialize resource cache fields to `None`. The facade must not duplicate experiment logic.

Implement `from_env` by composing `MLOpsConfig.from_env` with the normal constructor. Implement `user_agent` with `cls.sdk_name`; subclasses can override one class attribute rather than duplicating the method.

## Two distinct classmethod uses

Alternate constructor:

```python
client = MLOpsClient.from_env(mlflow_backend=backend)
```

Polymorphic access to class-wide metadata:

```python
class TeamClient(MLOpsClient):
    sdk_name = "team-mlops"

TeamClient.user_agent()  # team-mlops/0.1
```

Use an instance method when the answer depends on instance configuration. Use `@staticmethod` only when neither instance nor class is needed; often a module function is clearer.

## Common mistakes

- Constructing a real MLflow client inside `MLflowService` defeats injection.
- Putting `create_experiment` directly on the facade becomes cluttered as resources grow.
- Creating resources at module import time introduces global state.
- Returning a new resource on every property access loses caches and lifecycle state.

## Apply this to your SDK

Start with only the resource groups users genuinely need: perhaps `mlflow`, `bigquery`, and `pipelines`. Add sub-resources when a service becomes crowded. Avoid reproducing an entire provider's namespace.

## Check your understanding

- Where should credential resolution occur?
- Would four small services justify lazy properties? Why or why not?
- Why does `from_env` accept the backend instead of constructing it silently?

