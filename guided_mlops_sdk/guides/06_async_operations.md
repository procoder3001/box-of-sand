# Lesson 6: bounded and cancellable async operations

## When async helps an SDK

Async I/O is useful when one caller needs many independent network operations and the underlying client is genuinely asynchronous. It does not make CPU-bound model training faster, and wrapping a synchronous provider call in `async def` does not make it non-blocking.

Here you will fetch several runs concurrently while limiting pressure on the external service.

## Files to edit

1. Implement `MLflowService.get_runs` in `services/mlflow.py`.
2. Use the async method already declared by `MLflowBackend`.
3. Run `pytest -q tests/test_06_async_operations.py`.

## Implementation sequence

Validate `concurrency` and `timeout` before creating coroutines. Create one `asyncio.Semaphore(concurrency)` for this batch.

Define a nested async function for one run. Inside `async with semaphore`, call `asyncio.wait_for(backend.get_run_async(...), timeout)`. Translate `TimeoutError` to `MLOpsTimeoutError` with chaining, then adapt the response normally.

Use `asyncio.gather` on the per-run coroutines. `gather` returns results in input order even if requests complete out of order.

## Cancellation rule

Do not catch `BaseException`, and do not convert `asyncio.CancelledError` into a service error. Cancellation is control flow: callers use it to stop work during shutdown or abandoned requests. `async with semaphore` releases its permit while unwinding, and the backend coroutine's `finally` block handles its own state.

## Timeout versus retry

A timeout limits how long an attempt may take. A retry decides whether to attempt again. They are separate policies. This lesson adds no retry because retry safety depends on the operation:

- Reads are often safe to retry after transient failures.
- Writes may require idempotency keys or reconciliation.
- Provider retries and SDK retries can accidentally stack into a huge delay.

## Resource lifecycle

The backend exposes `aclose`, but this service does not automatically close the injected backend after each batch. The object that constructs and owns a long-lived backend should close it. Per-method cleanup would make connection pooling ineffective.

## Apply this to your SDK

Use bounded async operations for independent metadata reads, artifact checks, or status polling. Prefer the provider's native async client. If only a sync client exists, consciously choose threads for blocking I/O rather than hiding blocking calls in coroutines.

## Check your understanding

- Why is one semaphore created for the entire batch?
- What happens if cancellation is swallowed?
- When would streaming results with an async iterator be better than `gather`?

