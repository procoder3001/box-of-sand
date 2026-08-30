# Lesson 2: ports, adapters, and dependency injection

## The problem

If MLflow entity classes and exceptions leak throughout your package, every service and test becomes coupled to MLflow. An adapter gives that knowledge one home. A protocol describes the small capability your service needs without forcing test fakes or external clients to inherit from your code.

The flow is:

```text
external client/object → MLflowAdapter → mapping → validation → Run
```

## Protocol or ABC?

Use `Protocol` for `MLflowBackend` because the SDK does not own the external client and fakes should satisfy the contract structurally. There is no shared implementation to inherit.

An ABC would become useful for a family your SDK owns when the base supplies meaningful shared behavior or runtime registration. Do not create an ABC merely to obtain type annotations.

## Files to inspect and edit

1. Read `learner/src/company_mlops/ports.py`. Keep the protocol small.
2. Open `adapters/mlflow.py`.
3. Implement `adapt_run` using `MLflowRunPayload.model_validate`.
4. Implement `MLflowAdapter.__init__` and `get_run`.
5. Run `pytest -q tests/test_02_ports_and_adapters.py`.

## Important boundary choices

The adapter knows that the external object has `.info.run_id`. Nothing outside the adapter should know that. It flattens that shape into a mapping understood by the validator.

Translate only errors whose meaning you understand. Here, the fake vendor client uses `KeyError` for a missing run, so translate that to `RunNotFoundError` and chain the cause. Unknown errors should propagate rather than being mislabeled.

`adapt_run` then translates invalid response data to `TrackingError`. This gives SDK callers a stable exception family while keeping the diagnostic Pydantic cause.

## Why inject dependencies?

The adapter constructor receives a raw client instead of creating one. Construction often reads credentials, opens network pools, or depends on ambient configuration. Injection keeps those effects in the application composition root and lets tests use tiny fakes.

## Hints

- Store the injected client in `_raw_client`.
- Construct the mapping with exactly `run_id`, `experiment_id`, and `status` because extra fields are forbidden.
- Use two separate `try` blocks at the two separate boundaries; do not wrap every line in `except Exception`.

## Apply this to your SDK

Create comparable boundaries for BigQuery jobs, GCS blobs, Vertex operations, and MLflow runs only when you need insulation. Do not mirror every third-party object. Adapt the few objects that enter your public/domain API.

## Check your understanding

- Why is the protocol smaller than a real MLflow client?
- What would be lost if every service accepted `object`?
- Why can a fake satisfy `MLflowBackend` without subclassing it?
- When would returning the third-party object directly be a reasonable simpler choice?

