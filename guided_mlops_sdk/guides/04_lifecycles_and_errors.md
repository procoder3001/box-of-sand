# Lesson 4: run lifecycles and stable errors

## Why a context manager fits

A tracking run has paired operations and failure-dependent state:

```text
start → user work → FINISHED
                  ↘ exception → FAILED → re-raise
```

Requiring every caller to write `try/finally` duplicates policy and makes forgotten cleanup likely. A context manager packages that lifecycle without moving model training into the SDK.

## Files to edit

1. Read the hierarchy in `errors.py`.
2. Implement `ManagedRun` in `services/mlflow.py`.
3. Implement `MLflowService.run` so it only returns the manager.
4. Run `pytest -q tests/test_04_lifecycle_and_errors.py`.

## Implementation sequence

The constructor stores inputs but does not start a run. `__enter__` crosses the external boundary, records the run ID needed for cleanup, and returns a package-owned `Run`.

`__exit__` receives exception information. Choose `FINISHED` only when `exc_type is None`; otherwise choose `FAILED`. Call `end_run` and return `None` so an active user exception is not suppressed.

Starting in `__enter__` matters: merely creating a context-manager object should not mutate external state.

## Error ownership

Your package should expose a small hierarchy such as `MLOpsError`, `TrackingError`, and `RunNotFoundError`. This lets callers catch errors at the precision they need. Preserve underlying causes with `raise PackageError(...) from vendor_error`.

Do not translate programmer errors like `AttributeError` into friendly service errors. Broad translation destroys diagnostics.

## A deliberate simplification

The exercise assumes `end_run` itself succeeds. A production design must decide what happens when user work fails and cleanup also fails. Options include logging the cleanup failure, grouping exceptions, or allowing cleanup failure to replace the original. Document that policy and test it explicitly.

## Apply this to your SDK

Use context managers for MLflow runs, temporary workspaces, and owned sessions. Do not use them when your SDK does not own the resource lifecycle—for example, do not close an injected process-wide client unless ownership was transferred explicitly.

## Check your understanding

- Why does `run()` not call `start_run()` immediately?
- What would returning `True` from `__exit__` do?
- Who should own shutdown of a client injected by an application?

