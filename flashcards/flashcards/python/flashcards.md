### Front

A workflow framework must discover decorated steps before any flow instance exists. Why can a metaclass be justified here, and why is it probably excessive for a small deployment package?

```python
class TrainingFlow:
    def train(self) -> None: ...
```

### Back

A metaclass can inspect each subclass at class-creation time, build a graph once, and give every later instance consistent class-specific metadata. That enables a declarative user API. The cost is hidden execution during import, difficult debugging, inheritance edge cases, and tooling complexity. A small package should usually construct an explicit `Workflow` object or use a decorator that returns one.

```python
from dataclasses import dataclass
from collections.abc import Callable

@dataclass(frozen=True)
class Step:
    name: str
    run: Callable[[], None]

workflow = [Step("train", lambda: None)]
```

**Application:** Framework authors can justify class-construction hooks when the user-facing capability is “write a class and it becomes an executable DAG.” An internal MLOps package normally benefits more from explicit objects.

**When not to use:** Do not introduce a metaclass merely to register subclasses or validate a few fields; a factory, decorator, or `__init_subclass__` is clearer.

**Card ID:** C001
**Tags:** metaflow, metaclasses, workflow, overengineering
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `Netflix/metaflow` at commit `3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4`
**Source example:** [`metaflow/flowspec.py` — `FlowSpecMeta._init_attrs()`](https://github.com/Netflix/metaflow/blob/3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4/metaflow/flowspec.py#L166-L263)

---CARD---

### Front

Why does this dataclass accidentally share tags between instances?

```python
@dataclass
class RunConfig:
    tags: dict[str, str] = {}
```

### Back

Mutable defaults would be shared. Dataclasses reject common unhashable defaults; use `default_factory` to create one value per instance.

```python
from dataclasses import dataclass, field

@dataclass
class RunConfig:
    tags: dict[str, str] = field(default_factory=dict)
```

**Application:** Use factories for tags, options, artifact lists, and dependency collections.

**When not to use:** An immutable scalar or tuple can be a direct default.

**Card ID:** C049
**Tags:** dataclasses, defaults, default-factory, mutability
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python documentation — `dataclasses`](https://docs.python.org/3/library/dataclasses.html#default-factory-functions)
**Repository gap:** The corpus did not provide a clearer compact demonstration of the language rule than the official documentation.

---CARD---

### Front

What do `frozen=True` and `slots=True` mean for a value object?

```python
@dataclass(frozen=True, slots=True)
class ArtifactRef:
    uri: str
    digest: str
```

### Back

`frozen` prevents ordinary field assignment; `slots` generates slots and usually removes the per-instance dictionary. Together they express a compact value-like record, not deep immutability.

```python
ref = ArtifactRef("gs://bucket/model", "abc")
# ref.uri = "other"  # FrozenInstanceError
```

**Application:** Good for validated identifiers, resolved configuration snapshots, and operation handles.

**When not to use:** Mutable lifecycle entities and dynamic attribute needs should not be forced into frozen slots.

**Card ID:** C050
**Tags:** dataclasses, frozen-dataclasses, slots, value-objects
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python documentation — `dataclasses`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)
**Repository gap:** Repository uses did not isolate frozen/slots semantics as clearly as the official language documentation.

---CARD---

### Front

When is a frozen dataclass hashable, and what can still go wrong?

```python
@dataclass(frozen=True)
class Key:
    parts: list[str]
```

### Back

Generated equality compares fields; safe generated hashing generally requires frozen equality semantics. But a list field is itself unhashable and can still be mutated, so “frozen” is shallow.

```python
@dataclass(frozen=True)
class Key:
    parts: tuple[str, ...]

cache: dict[Key, bytes] = {}
```

**Application:** Hashable configuration keys support memoization only when all equality-relevant state is stable.

**When not to use:** Do not set `unsafe_hash=True` to silence a design problem.

**Card ID:** C051
**Tags:** dataclasses, equality, hashing, immutability
**Difficulty:** Advanced
**Source type:** Official documentation
**Source:** [Python documentation — dataclass hash rules](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)
**Repository gap:** The corpus lacked a concise transferable example covering the interaction of equality, hashing, and mutable fields.

---CARD---

### Front

When is a property better than a public field?

```python
config.timeout_seconds = -1
```

### Back

A property is useful when attribute-shaped access needs computation, validation, or compatibility. Keep simple data simple.

```python
class Config:
    def __init__(self, timeout: float) -> None:
        self._timeout = timeout

    @property
    def timeout(self) -> float:
        return self._timeout
```

**Application:** A property can preserve an old public attribute while internal representation changes.

**When not to use:** Do not hide network I/O or expensive work behind innocent-looking attribute access.

**Card ID:** C052
**Tags:** properties, public-api, compatibility, encapsulation
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python documentation — `property`](https://docs.python.org/3/library/functions.html#property)
**Repository gap:** Repository examples mixed properties with framework-specific behavior; official docs provide the direct semantic basis.

---CARD---

### Front

How does an async context manager clean up a streaming resource?

```python
stream = await client.open_stream()
data = await stream.read()
```

### Back

`async with` awaits entry and exit, so cleanup can itself perform asynchronous I/O even on failure.

```python
class Stream:
    async def __aenter__(self) -> "Stream":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

async with client.open_stream() as stream:
    data = await stream.read()
```

**Application:** Use for async HTTP streams, sessions, leases, and temporary cloud resources.

**When not to use:** A resource with synchronous cleanup needs only a normal context manager.

**Card ID:** C053
**Tags:** async-context-managers, cleanup, streaming, resource-lifecycle
**Difficulty:** Advanced
**Source type:** Official documentation
**Source:** [Python documentation — asynchronous context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
**Repository gap:** SDK examples showed lifecycle use, but the official language reference most directly defines `__aenter__` and `__aexit__` semantics.

---CARD---

### Front

What should happen when an async artifact task is cancelled?

```python
async def upload() -> None:
    try:
        await send_chunks()
    except BaseException:
        return
```

### Back

Cleanup should run, then cancellation should propagate. Swallowing it prevents cooperative shutdown.

```python
async def upload() -> None:
    session = await open_session()
    try:
        await send_chunks(session)
    finally:
        await session.aclose()
```

**Application:** Do not classify cancellation as an ordinary retryable service error.

**When not to use:** Shield a tiny critical cleanup section only with a documented consistency reason.

**Card ID:** C054
**Tags:** async, cancellation, cleanup, retries
**Difficulty:** Advanced
**Source type:** Official documentation
**Source:** [Python documentation — task cancellation](https://docs.python.org/3/library/asyncio-task.html#task-cancellation)
**Repository gap:** Corpus tests exercised async failure cleanup, but precise cancellation semantics are language/runtime behavior best sourced officially.

---CARD---

### Front

Choose threads, processes, or async I/O for three tasks: many HTTP calls, CPU-heavy model conversion, and wrapping a blocking SDK.

```python
jobs = [download(u) for u in uris]
```

### Back

Use async I/O for many natively async network operations, processes for CPU-bound Python work that benefits from parallel cores, and a bounded thread pool to integrate blocking I/O without blocking an event loop.

```python
result = await asyncio.to_thread(blocking_client.download, uri)
```

**Application:** Measure first; serialization cost and SDK thread safety affect the choice.

**When not to use:** Sequential code is often best for low volume.

**Card ID:** C055
**Tags:** concurrency, threads, processes, async-io
**Difficulty:** Advanced
**Source type:** Official documentation
**Source:** [Python documentation — concurrency and multithreading](https://docs.python.org/3/library/asyncio-task.html#running-in-threads)
**Repository gap:** No single repository source made the general three-way selection rule explicit.

---CARD---

### Front

How should optional integrations fail?

```python
import google.cloud.storage  # package import now fails for every user
```

### Back

Import an optional dependency at the feature boundary and raise an actionable package error. Declare extras so users can install the capability intentionally.

```python
def gcs_store() -> "Store":
    try:
        from google.cloud import storage
    except ImportError as exc:
        raise RuntimeError("install package[gcs]") from exc
    return GcsStore(storage.Client())
```

**Application:** Core library and CLI `--help` remain usable without every provider SDK.

**When not to use:** A dependency required by every supported workflow should be mandatory.

**Card ID:** C056
**Tags:** optional-dependencies, import-boundaries, packaging, errors
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python Packaging User Guide — dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#extras)
**Repository gap:** Repositories demonstrate optional integrations, while the packaging specification directly supports extras declaration semantics.

---CARD---

### Front

How does `pyproject.toml` expose a Click command without executing expensive work at installation/import time?

```toml
[project.scripts]
mlops = "mlops.cli:main"
```

### Back

The installer creates a console-script wrapper that imports and calls the named function. Keep module import cheap; configure logging and construct clients inside `main` or the command composition root.

```python
def main() -> None:
    configure_logging()
    cli()
```

**Application:** The same package remains importable as a library, while the CLI is an adapter entry point.

**When not to use:** Do not create a console script for functionality intended only as a Python API.

**Card ID:** C057
**Tags:** pyproject, click, entry-points, import-side-effects
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python Packaging User Guide — creating and packaging command-line tools](https://packaging.python.org/en/latest/guides/creating-command-line-tools/)
**Repository gap:** Click implements commands but does not define packaging metadata semantics.

---CARD---

### Front

How can a package deprecate `old_timeout` without silently breaking callers?

```python
Client(old_timeout=10)
```

### Back

Accept the old name for a documented transition, warn with a caller-facing stack level, reject conflicts, and translate to the new representation.

```python
import warnings

def Client(*, timeout=None, old_timeout=None):
    if timeout is not None and old_timeout is not None:
        raise TypeError("choose timeout or old_timeout")
    if old_timeout is not None:
        warnings.warn("old_timeout is deprecated", DeprecationWarning, stacklevel=2)
        timeout = old_timeout
```

**Application:** Test warning category/message and both compatibility paths.

**When not to use:** Security flaws may require immediate breaking removal with clear release notes.

**Card ID:** C058
**Tags:** backward-compatibility, deprecation, warnings, public-api
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python documentation — warning categories](https://docs.python.org/3/library/exceptions.html#DeprecationWarning)
**Repository gap:** Corpus contains compatibility mechanisms, but official docs precisely define user-facing deprecation categories.

---CARD---

### Front

Why is untrusted pickle unsafe for artifact deserialization?

```python
model = pickle.loads(downloaded_bytes)
```

### Back

Pickle can execute arbitrary code during loading. Treat it as trusted-code loading, verify provenance/integrity, and prefer constrained formats for untrusted exchange.

```python
import json

metadata = json.loads(downloaded_bytes)
validate_metadata(metadata)
```

**Application:** Record serializer format/version and digest alongside artifacts; validate before constructing domain objects.

**When not to use:** Pickle may be acceptable inside a strictly trusted controlled boundary with explicit risk ownership.

**Card ID:** C059
**Tags:** serialization, security, validation, artifacts
**Difficulty:** Advanced
**Source type:** Official documentation
**Source:** [Python documentation — `pickle` warning](https://docs.python.org/3/library/pickle.html#module-pickle)
**Repository gap:** Repository serializers are framework-specific; official documentation directly establishes the security property.

---CARD---

### Front

When do hooks provide more value than callbacks, registries, or dependency injection?

```python
hooks.before_deploy(spec)
hooks.after_deploy(result)
```

### Back

Hooks fit multiple independent extensions participating at named lifecycle points under a stable contract. A registry selects an implementation; a callback handles one event; dependency injection supplies a collaborator.

```python
class DeployHooks(Protocol):
    def before_deploy(self, spec: "Spec") -> None: ...

def deploy(spec: "Spec", hooks: list[DeployHooks]) -> None:
    for hook in hooks:
        hook.before_deploy(spec)
```

**Application:** Start with injected callbacks or a dictionary; add discovery only for independently distributed extensions.

**When not to use:** Most internal packages do not need a plugin ecosystem.

**Card ID:** C060
**Tags:** plugins, hooks, callbacks, dependency-injection
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/store/artifact/artifact_repository_registry.py` — `register_entrypoints()`](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/store/artifact/artifact_repository_registry.py#L39-L57)

---CARD---

### Front

Why represent retry rules as callable strategy objects?

```python
rule = RetryIfException((TimeoutError, ConnectionError))
if rule(state): ...
```

### Back

An object stores configuration while sharing a simple callable contract. Plain predicate functions can remain valid for one-off rules.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryStatus:
    statuses: frozenset[int]
    def __call__(self, status: int) -> bool:
        return status in self.statuses
```

**Application:** Inject retry, wait, stop, sleep, and callbacks; unit-test each without real network calls or delays.

**When not to use:** A small bounded loop is enough for one known transient call; use an established library in production.

**Card ID:** C039
**Tags:** tenacity, callable-objects, strategies, dataclasses
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `jd/tenacity` at commit `b3c5a9f9212187aaf96353378daa9a9ebd800742`
**Source example:** [`tenacity/__init__.py` — `BaseRetrying.__init__`](https://github.com/jd/tenacity/blob/b3c5a9f9212187aaf96353378daa9a9ebd800742/tenacity/__init__.py#L237-L265)

---CARD---

### Front

What does explicit retry state buy you?

```python
callback(attempt=3, error=exc, elapsed=8.2)
```

### Back

A state object makes policy inputs, callbacks, observations, and tests coherent without scattered local variables.

```python
from dataclasses import dataclass

@dataclass
class AttemptState:
    number: int
    elapsed: float
    outcome: object | None = None
```

**Application:** Log attempt number, elapsed time, next delay, operation, and exception class—but no secrets or full request bodies.

**When not to use:** Do not expose a large mutable state object if a predicate needs only an exception.

**Card ID:** C040
**Tags:** tenacity, state, callbacks, testability
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `jd/tenacity` at commit `b3c5a9f9212187aaf96353378daa9a9ebd800742`
**Source example:** [`tenacity/__init__.py` — `RetryCallState`](https://github.com/jd/tenacity/blob/b3c5a9f9212187aaf96353378daa9a9ebd800742/tenacity/__init__.py#L567-L616)

---CARD---

### Front

What is risky about clever retry-rule composition?

```python
rule = transient & has_key | server_says_retry
```

### Back

Operator precedence and side-effect safety can become hard to audit. Compose small rules only when their truth table is clear; otherwise use a named predicate.

```python
def safe_to_retry(state: "State") -> bool:
    return state.transient and state.operation_id is not None
```

**Application:** Test combinations directly: transient/permanent × committed/uncommitted × budget remaining/exhausted.

**When not to use:** Prefer explicit conditionals around dangerous writes.

**Card ID:** C041
**Tags:** tenacity, composition, predicates, retry-safety
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `jd/tenacity` at commit `b3c5a9f9212187aaf96353378daa9a9ebd800742`
**Source example:** [`tenacity/retry.py` — `retry_base` composition operators](https://github.com/jd/tenacity/blob/b3c5a9f9212187aaf96353378daa9a9ebd800742/tenacity/retry.py#L25-L61)
**Related test:** [`tests/test_tenacity.py` — callable composition tests](https://github.com/jd/tenacity/blob/b3c5a9f9212187aaf96353378daa9a9ebd800742/tests/test_tenacity.py#L801-L849)

---CARD---

### Front

Why should retry state be copied per decorated invocation?

```python
@retry(...)
def fetch(name: str): ...
```

### Back

Shared mutable attempt state leaks across concurrent or recursive calls. Configuration can be shared; execution state cannot.

```python
def wrapped(*args, **kwargs):
    controller = configured_controller.copy()
    return controller.call(fn, *args, **kwargs)
```

**Application:** Independently test two interleaved calls and ensure attempt counters do not contaminate one another.

**When not to use:** Immutable stateless predicates can be safely shared.

**Card ID:** C042
**Tags:** decorators, concurrency, state, thread-safety
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `jd/tenacity` at commit `b3c5a9f9212187aaf96353378daa9a9ebd800742`
**Source example:** [`tenacity/__init__.py` — `BaseRetrying.wraps()`](https://github.com/jd/tenacity/blob/b3c5a9f9212187aaf96353378daa9a9ebd800742/tenacity/__init__.py#L357-L390)

---CARD---

### Front

How should retry exhaustion surface from a package API?

```python
raise RetryFrameworkError(last_attempt)
```

### Back

Usually re-raise the last package/domain exception so callers are not coupled to retry machinery, while retaining chaining and attempt diagnostics in logs.

```python
try:
    retrying.call(read_model)
except RetryError as exc:
    raise exc.last_attempt.exception()
```

**Application:** A CLI can still translate `TransientServiceError`; changing retry libraries does not break callers.

**When not to use:** A retry-specific exception is useful when callers genuinely need aggregate attempt information.

**Card ID:** C043
**Tags:** retries, exception-chaining, public-api, compatibility
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `jd/tenacity` at commit `b3c5a9f9212187aaf96353378daa9a9ebd800742`
**Source example:** [`tests/test_tenacity.py` — `test_reraise_by_default`](https://github.com/jd/tenacity/blob/b3c5a9f9212187aaf96353378daa9a9ebd800742/tests/test_tenacity.py#L1880-L1894)

---CARD---

### Front

Why derive a bound logger instead of mutating shared context?

```python
base.bind(run_id="r1")
```

### Back

Binding should return a new logger with copied context, preventing one concurrent job’s fields from contaminating another.

```python
base = log.bind(service="deployer", environment="prod")
run_log = base.bind(run_id="r1", model="fraud-v3")
run_log.info("deployment_started")
```

**Application:** Bind pipeline, run, job, deployment, trace, and cloud request IDs at their natural scopes.

**When not to use:** `logging.LoggerAdapter` or explicit `extra` may suffice for a small synchronous package.

**Card ID:** C044
**Tags:** structlog, structured-logging, bound-loggers, immutable-context
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `hynek/structlog` at commit `7b04229f3e569d03f5b8a7ae919355a3a0e0abb2`
**Source example:** [`src/structlog/_base.py` — `BoundLoggerBase.bind()`](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/src/structlog/_base.py#L28-L107)
**Related test:** [`tests/test_base.py` — immutable binding](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/tests/test_base.py#L40-L49)

---CARD---

### Front

Why does processor ordering matter in structured logging?

```python
processors = [JSONRenderer(), redact_secrets]
```

### Back

Each processor transforms the previous result. Rendering usually terminates dictionary processing, so redact and enrich before rendering.

```python
processors = [
    merge_context,
    add_timestamp,
    redact_secrets,
    JSONRenderer(),
]
```

**Application:** Unit-test processors individually and one configured pipeline.

**When not to use:** A fixed standard logging formatter is simpler if structured transformation is unnecessary.

**Card ID:** C045
**Tags:** structlog, processors, composition, structured-logging
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `hynek/structlog` at commit `7b04229f3e569d03f5b8a7ae919355a3a0e0abb2`
**Source example:** [`src/structlog/_base.py` — processor pipeline](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/src/structlog/_base.py#L165-L191)

---CARD---

### Front

What must secret-redaction tests cover beyond a top-level `token` key?

```python
event["token"] = "[redacted]"
```

### Back

Secrets can appear in nested mappings, headers, URLs, exceptions, object representations, and free-form messages. Prevention and allowlists are stronger than chasing every key.

```python
SAFE_FIELDS = {"event", "run_id", "status", "request_id"}

def allowlist(event: dict[str, object]) -> dict[str, object]:
    return {k: v for k, v in event.items() if k in SAFE_FIELDS}
```

**Application:** Assert a sentinel credential is absent from serialized logs.

**When not to use:** Do not discard operational fields indiscriminately; design a documented event schema.

**Card ID:** C046
**Tags:** structured-logging, redaction, secrets, testing
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `hynek/structlog` at commit `7b04229f3e569d03f5b8a7ae919355a3a0e0abb2`
**Source example:** [`src/structlog/_base.py` — `_process_event()`](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/src/structlog/_base.py#L123-L191)

---CARD---

### Front

When are `contextvars` appropriate for run metadata?

```python
current_run_id = "r1"  # global
```

### Back

They carry task-local cross-cutting context through async calls without process-global contamination. Tokens/context managers restore prior values precisely.

```python
from structlog.contextvars import bound_contextvars

async def execute(run_id: str) -> None:
    with bound_contextvars(run_id=run_id):
        await train()
```

**Application:** Use for observability metadata, not hidden business inputs. Explicitly serialize IDs into queued work; context does not magically cross processes.

**When not to use:** Passing a bound logger is clearer in straightforward synchronous code.

**Card ID:** C047
**Tags:** contextvars, async, structured-logging, execution-context
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `hynek/structlog` at commit `7b04229f3e569d03f5b8a7ae919355a3a0e0abb2`
**Source example:** [`src/structlog/contextvars.py` — `bind_contextvars()` and `reset_contextvars()`](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/src/structlog/contextvars.py#L119-L157)
**Related test:** [`tests/test_contextvars.py` — async inheritance and reset](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/tests/test_contextvars.py#L35-L107)

---CARD---

### Front

How should structured logging be tested?

```python
assert "2026-... INFO deployment_started" == output
```

### Back

Assert event data and secret absence, not unstable timestamps or human formatting. Restore global configuration even when a test fails.

```python
with capture_logs() as events:
    log.info("deployment_started", run_id="r7")

assert events[0]["event"] == "deployment_started"
assert events[0]["run_id"] == "r7"
assert "access_token" not in events[0]
```

**Application:** Use an integration test only for the final renderer/handler path.

**When not to use:** Beware global capture helpers in parallel threads; isolate configuration.

**Card ID:** C048
**Tags:** structured-logging, unit-testing, global-state, cleanup
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `hynek/structlog` at commit `7b04229f3e569d03f5b8a7ae919355a3a0e0abb2`
**Source example:** [`src/structlog/testing.py` — `capture_logs()`](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/src/structlog/testing.py#L50-L100)
**Related test:** [`tests/test_testing.py` — restoration on error](https://github.com/hynek/structlog/blob/7b04229f3e569d03f5b8a7ae919355a3a0e0abb2/tests/test_testing.py#L42-L92)

---CARD---

### Front

Where should a Click command’s business logic live?

```python
@click.command()
def deploy() -> None:
    # validation, cloud calls, polling, logging, persistence...
    ...
```

### Back

The command should parse CLI input, call a Click-free public API/service, render the result, and translate expected domain errors.

```python
@click.command()
@click.option("--model", required=True)
@click.pass_obj
def deploy(app: "App", model: str) -> None:
    result = app.deployments.deploy(model)
    click.echo(result.id)
```

**Application:** Library callers, CLI callers, and tests share the same behavior without invoking Click.

**When not to use:** Trivial presentation-only commands need no elaborate service layer.

**Card ID:** C026
**Tags:** click, cli-library-separation, dependency-injection, public-api
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `pallets/click` at commit `00e592cea702e0b2caa0dee42489fdb1c22cd845`
**Source example:** [`src/click/decorators.py` — `pass_obj`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/src/click/decorators.py#L20-L97)

---CARD---

### Front

What belongs in `ctx.obj`?

```python
ctx.obj = {"run_id": None, "status": None, "artifacts": []}
```

### Back

Use it as a small composition container for dependencies and resolved configuration, not as the mutable domain model.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class App:
    deployments: "DeploymentService"
    config: "Config"
```

**Application:** The group builds `App`; subcommands receive it and delegate.

**When not to use:** Directly pass one dependency when there is no command group or shared invocation state.

**Card ID:** C027
**Tags:** click, context, dependency-injection, dataclasses
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `pallets/click` at commit `00e592cea702e0b2caa0dee42489fdb1c22cd845`
**Source example:** [`src/click/core.py` — `Context.find_object()`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/src/click/core.py#L740-L759)
**Related test:** [`tests/test_context.py` — context object injection](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/tests/test_context.py#L17-L103)

---CARD---

### Front

How should the CLI translate an expected domain error?

```python
try:
    service.deploy(model)
except Exception:
    raise click.ClickException("failed")
```

### Back

Catch only package-owned expected errors, provide a safe actionable message, and chain the cause. Let unexpected bugs retain tracebacks.

```python
try:
    service.deploy(model)
except DeploymentConflict as exc:
    raise click.ClickException(str(exc)) from exc
```

**Application:** The domain layer never imports Click; the adapter controls stderr and exit status.

**When not to use:** Do not turn every internal exception into a generic exit code.

**Card ID:** C028
**Tags:** click, exception-translation, exit-codes, stderr
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `pallets/click` at commit `00e592cea702e0b2caa0dee42489fdb1c22cd845`
**Source example:** [`src/click/core.py` — `Context.fail()` and `Context.exit()`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/src/click/core.py#L807-L827)

---CARD---

### Front

How do parse errors differ from domain errors?

```python
# Shell input: deploy --replicas many
argv = ["deploy", "--replicas", "many"]
```

### Back

Click validates syntax/types before invocation and produces usage errors. The service validates domain rules after parsing and raises package exceptions.

```python
@click.option("--replicas", type=click.IntRange(min=1))
def deploy(replicas: int) -> None:
    service.deploy(replicas)  # may reject quota or deployment state
```

**Application:** Test CLI parsing separately from service invariants.

**When not to use:** Avoid duplicating the same validation in both layers; put only presentation-shaped validation in Click.

**Card ID:** C029
**Tags:** click, validation, error-handling, layering
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `pallets/click` at commit `00e592cea702e0b2caa0dee42489fdb1c22cd845`
**Source example:** [`src/click/core.py` — `Command.parse_args()`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/src/click/core.py#L1358-L1408)

---CARD---

### Front

How should one command invocation share and clean up a client?

```python
client = CloudClient()
run_subcommand(client)
```

### Back

Register a context-managed resource on Click’s context exit stack so cleanup runs after success or failure.

```python
@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.obj = ctx.with_resource(CloudClient())
```

**Application:** Share one MLflow/GCP session across a command tree while preserving deterministic teardown.

**When not to use:** A short `with` inside one service method is clearer when nothing is shared.

**Card ID:** C030
**Tags:** click, context-managers, cleanup, resource-lifecycle
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `pallets/click` at commit `00e592cea702e0b2caa0dee42489fdb1c22cd845`
**Source example:** [`src/click/core.py` — `Context.with_resource()`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/src/click/core.py#L648-L675)
**Related test:** [`tests/test_context.py` — `test_with_resource_exception`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/tests/test_context.py#L522-L589)

---CARD---

### Front

What should a `CliRunner` test prove?

```python
result = runner.invoke(cli, ["deploy", "model-a"])
```

### Back

Test argv/env parsing, dependency wiring, output stream, exit code, and domain-error translation. Inject a fake service; test most business behavior directly through the library API.

```python
fake = FakeDeployments(result_id="dep-1")
result = runner.invoke(cli, ["deploy", "model-a"], obj=App(fake, config))
assert result.exit_code == 0
assert result.output == "dep-1\n"
```

**Application:** No CLI unit test should contact GCP or MLflow.

**When not to use:** Do not route every service test through Click.

**Card ID:** C031
**Tags:** click, cli-testing, fakes, unit-testing
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `pallets/click` at commit `00e592cea702e0b2caa0dee42489fdb1c22cd845`
**Source example:** [`src/click/testing.py` — `CliRunner.invoke()`](https://github.com/pallets/click/blob/00e592cea702e0b2caa0dee42489fdb1c22cd845/src/click/testing.py#L596-L688)

---CARD---

### Front

When should a storage contract be a `Protocol` versus an ABC?

```python
class ArtifactStore(Protocol):
    def read(self, uri: str) -> bytes: ...
```

### Back

Use a `Protocol` for structural typing and lightweight fakes. Use an ABC when nominal membership, shared implementation, or preventing incomplete instantiation matters.

```python
from abc import ABC, abstractmethod

class ArtifactStoreABC(ABC):
    @abstractmethod
    def read(self, uri: str) -> bytes: ...
```

**Application:** A narrow protocol often fits local/GCS artifact adapters better than exposing a huge filesystem API.

**When not to use:** Two simple injected functions may need neither.

**Card ID:** C032
**Tags:** protocol, abc, typing, adapters
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `fsspec/filesystem_spec` at commit `669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55`
**Source example:** [`fsspec/spec.py` — `AbstractFileSystem`](https://github.com/fsspec/filesystem_spec/blob/669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55/fsspec/spec.py#L150-L209)

---CARD---

### Front

What should contract tests verify across local and cloud storage adapters?

```python
def test_store(store: ArtifactStore) -> None:
    ...
```

### Back

Run the same behavioral assertions for path normalization, missing objects, listing shape, overwrite rules, and cleanup. Use memory/local adapters in unit tests and a small real-cloud integration suite.

```python
def assert_store_contract(store: "ArtifactStore") -> None:
    store.write("runs/1/model.bin", b"x")
    assert store.read("runs/1/model.bin") == b"x"
    assert "runs/1/model.bin" in store.list("runs/1")
```

**Application:** This catches semantic drift between GCS and local development behavior.

**When not to use:** Provider-specific capabilities deserve separate tests rather than weakening the common contract.

**Card ID:** C033
**Tags:** contract-testing, adapters, storage, integration-testing
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `fsspec/filesystem_spec` at commit `669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55`
**Source example:** [`fsspec/spec.py` — `AbstractFileSystem.ls()`](https://github.com/fsspec/filesystem_spec/blob/669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55/fsspec/spec.py#L374-L405)

---CARD---

### Front

Why is `asyncio.run()` a poor generic sync/async bridge inside library code?

```python
def read(uri: str) -> bytes:
    return asyncio.run(aread(uri))
```

### Back

It cannot run inside an already-running event loop and obscures loop/thread ownership. Prefer separate public surfaces or a carefully owned background-loop bridge.

```python
class Store:
    def read(self, uri: str) -> bytes: ...

class AsyncStore:
    async def read(self, uri: str) -> bytes: ...
```

**Application:** Share request-building logic, not event-loop control.

**When not to use:** A command-line-only package may need only sync I/O.

**Card ID:** C034
**Tags:** async, sync-async-boundary, event-loops, storage
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `fsspec/filesystem_spec` at commit `669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55`
**Source example:** [`fsspec/asyn.py` — `sync()` and `sync_wrapper()`](https://github.com/fsspec/filesystem_spec/blob/669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55/fsspec/asyn.py#L63-L119)

---CARD---

### Front

How do you bound concurrent artifact downloads?

```python
await asyncio.gather(*(download(x) for x in thousands))
```

### Back

Use a semaphore or chunked scheduler, propagate the first failure, and cancel/await pending tasks so resources are reclaimed.

```python
import asyncio

sem = asyncio.Semaphore(10)

async def bounded(uri: str) -> bytes:
    async with sem:
        return await download(uri)
```

**Application:** Bounded concurrency protects sockets, memory, rate limits, and GCS quotas.

**When not to use:** Sequential I/O is simpler for a few small objects.

**Card ID:** C035
**Tags:** async, bounded-concurrency, cancellation, batching
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `fsspec/filesystem_spec` at commit `669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55`
**Source example:** [`fsspec/asyn.py` — `_run_coros_in_chunks()`](https://github.com/fsspec/filesystem_spec/blob/669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55/fsspec/asyn.py#L220-L294)
**Related test:** [`fsspec/tests/test_async.py` — `test_run_coros_in_chunks`](https://github.com/fsspec/filesystem_spec/blob/669de5e157cd3ce3f9bf71c7bceb7bb31c8c7a55/fsspec/tests/test_async.py#L98-L138)

---CARD---

### Front

Why protect credential refresh with a lock and re-check after acquiring it?

```python
if token.expired:
    token.refresh()
```

### Back

Concurrent callers can all observe expiry. One refreshes under the lock; later callers re-check and reuse the fresh token.

```python
with refresh_lock:
    if token.expired:  # double-check
        token.refresh()
```

**Application:** Usually let the provider auth library own this; test with fake credentials and never log token values.

**When not to use:** Do not implement custom refresh when Application Default Credentials already solve it.

**Card ID:** C036
**Tags:** authentication, concurrency, locking, secrets
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `fsspec/gcsfs` at commit `8ad3852f09e2330e470edbf57a47432e50ec0828`
**Source example:** [`gcsfs/credentials.py` — `maybe_refresh()`](https://github.com/fsspec/gcsfs/blob/8ad3852f09e2330e470edbf57a47432e50ec0828/gcsfs/credentials.py#L220-L285)
**Related test:** [`gcsfs/tests/test_credentials.py` — expiry behavior](https://github.com/fsspec/gcsfs/blob/8ad3852f09e2330e470edbf57a47432e50ec0828/gcsfs/tests/test_credentials.py#L185-L210)

---CARD---

### Front

Why must a retrying upload rewind a seekable request body?

```python
for attempt in range(3):
    await http.put(url, data=file_obj)
```

### Back

The first attempt consumes the stream. Later attempts otherwise send only the remaining bytes—often an empty or corrupt upload.

```python
start = file_obj.tell()
for attempt in range(3):
    file_obj.seek(start)
    await http.put(url, data=file_obj)
```

**Application:** Retry safety includes replayable inputs as well as idempotent server effects.

**When not to use:** A non-seekable stream should be buffered deliberately or treated as non-retryable.

**Card ID:** C037
**Tags:** retries, serialization, streams, idempotency
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `fsspec/gcsfs` at commit `8ad3852f09e2330e470edbf57a47432e50ec0828`
**Source example:** [`gcsfs/core.py` — `_request()`](https://github.com/fsspec/gcsfs/blob/8ad3852f09e2330e470edbf57a47432e50ec0828/gcsfs/core.py#L492-L522)

---CARD---

### Front

What is the hard part of caching remote directory listings?

```python
@cache
def list_objects(prefix: str) -> list[str]: ...
```

### Back

Invalidation: writes, deletes, other processes, and expiration can make cached listings stale. Define freshness and explicit invalidation behavior.

```python
def write(path: str, data: bytes) -> None:
    remote_write(path, data)
    listing_cache.pop(parent(path), None)
```

**Application:** Cache expensive artifact listings only when callers tolerate bounded staleness.

**When not to use:** Skip caching when correctness requires read-after-write visibility and calls are infrequent.

**Card ID:** C038
**Tags:** caching, storage, consistency, resource-management
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `fsspec/gcsfs` at commit `8ad3852f09e2330e470edbf57a47432e50ec0828`
**Source example:** [`gcsfs/core.py` — listing cache documentation](https://github.com/fsspec/gcsfs/blob/8ad3852f09e2330e470edbf57a47432e50ec0828/gcsfs/core.py#L240-L253)

---CARD---
 
### Front

Why should constructing a service client avoid contacting the network or importing runtime-specific integrations?

```python
class Client:
    def __init__(self) -> None:
        self.identity = discover_cloud_identity()
```

### Back

Construction becomes slow, failure-prone, and unsafe at import time. Keep it cheap; resolve optional/stateful facilities lazily or through explicit methods.

```python
from functools import cached_property

class Client:
    @cached_property
    def cloud_tools(self) -> "CloudTools":
        return CloudTools.discover()
```

**Application:** Tests can instantiate a client without credentials; CLI startup and `--help` remain fast.

**When not to use:** Eagerly validate pure local values when failure should be immediate.

**Card ID:** C011
**Tags:** clients, lazy-evaluation, import-boundaries, side-effects
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `databricks/databricks-sdk-py` at commit `1b51dbda48200e1ab6fd89ff951bea888a765260`
**Source example:** [`databricks/sdk/__init__.py` — `WorkspaceClient.__init__`](https://github.com/databricks/databricks-sdk-py/blob/1b51dbda48200e1ab6fd89ff951bea888a765260/databricks/sdk/__init__.py#L289-L366)
**Related test:** [`tests/test_client.py` — `test_workspace_client_init_does_not_build_dbutils`](https://github.com/databricks/databricks-sdk-py/blob/1b51dbda48200e1ab6fd89ff951bea888a765260/tests/test_client.py#L31-L37)

---CARD---

### Front

When do separate capability-scoped clients beat one “god client”?

```python
client.workspace.delete_user("x")
client.account.start_cluster("y")
```

### Back

Separate clients make invalid operations harder to express and clarify configuration scope, while sharing a transport internally.

```python
class WorkspaceClient:
    def __init__(self, transport: "Transport") -> None:
        self.jobs = JobService(transport)

class AdminClient:
    def __init__(self, transport: "Transport") -> None:
        self.projects = ProjectService(transport)
```

**Application:** Split deployment-control operations from experiment-tracking operations if they have different credentials and audiences.

**When not to use:** A handful of cohesive operations should stay on one small client.

**Card ID:** C012
**Tags:** clients, public-api, composition, capability-design
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `databricks/databricks-sdk-py` at commit `1b51dbda48200e1ab6fd89ff951bea888a765260`
**Source example:** [`databricks/sdk/__init__.py` — `WorkspaceClient` and `AccountClient`](https://github.com/databricks/databricks-sdk-py/blob/1b51dbda48200e1ab6fd89ff951bea888a765260/databricks/sdk/__init__.py#L289-L366)

---CARD---

### Front

What application-oriented problem can a descriptor solve in configuration?

```python
class Config:
    token = ConfigField(env="SERVICE_TOKEN", sensitive=True)
```

### Back

A descriptor centralizes behavior for attribute access: conversion, metadata, validation, and secret-aware representation. It is useful when many fields share rich rules.

```python
class ConfigField:
    def __init__(self, *, sensitive: bool = False) -> None:
        self.sensitive = sensitive

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: object, owner: type) -> object:
        return obj.__dict__[self.name]
```

**Application:** It can encode environment names and sensitivity consistently across a large SDK configuration surface.

**When not to use:** For ten settings, a frozen dataclass plus resolver is easier to read and type-check.

**Card ID:** C013
**Tags:** descriptors, configuration, secrets, overengineering
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `databricks/databricks-sdk-py` at commit `1b51dbda48200e1ab6fd89ff951bea888a765260`
**Source example:** [`databricks/sdk/config.py` — `ConfigAttribute`](https://github.com/databricks/databricks-sdk-py/blob/1b51dbda48200e1ab6fd89ff951bea888a765260/databricks/sdk/config.py#L30-L56)

---CARD---

### Front

Why model a long-running deployment as an operation handle instead of blocking inside `deploy()`?

```python
result = deploy(model)  # blocks for 40 minutes
```

### Back

Submission and waiting are different phases. A handle exposes the operation ID, lets callers select a deadline, resume polling, or cancel.

```python
from dataclasses import dataclass
from datetime import timedelta
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class Operation(Generic[T]):
    id: str
    def wait(self, timeout: timedelta) -> T: ...
```

**Application:** A Click command may wait and render progress, while library callers can schedule or persist the handle.

**When not to use:** A fast, single synchronous RPC does not need this lifecycle.

**Card ID:** C014
**Tags:** generics, long-running-operations, timeouts, public-api
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `databricks/databricks-sdk-py` at commit `1b51dbda48200e1ab6fd89ff951bea888a765260`
**Source example:** [`databricks/sdk/service/_internal.py` — `Wait`](https://github.com/databricks/databricks-sdk-py/blob/1b51dbda48200e1ab6fd89ff951bea888a765260/databricks/sdk/service/_internal.py#L141-L163)

---CARD---

### Front

Why prefer an explicit client over module-level mutable configuration?

```python
sdk.api_key = token
sdk.deploy(model)
```

### Back

Globals prevent independent configurations in one process, leak state between tests, and make concurrency surprising. An explicit client owns configuration and dependencies.

```python
class DeploymentClient:
    def __init__(self, token: str, http: "HttpClient") -> None:
        self._token = token
        self._http = http

dev = DeploymentClient(dev_token, fake_http)
prod = DeploymentClient(prod_token, real_http)
```

**Application:** Pass the client into services; let Click’s composition root construct it once.

**When not to use:** A pure stateless module needs no client object.

**Card ID:** C015
**Tags:** clients, dependency-injection, global-state, testing
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `stripe/stripe-python` at commit `07b9a74cf02ce55413237a434be807190fccc3a7`
**Source example:** [`stripe/_stripe_client.py` — `StripeClient.__init__`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/stripe/_stripe_client.py#L136-L195)
**Related test:** [`tests/test_api_requestor.py` — `test_sets_default_http_client`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/tests/test_api_requestor.py#L656-L673)

---CARD---

### Front

Why reject both an injected HTTP client and low-level proxy/TLS options?

```python
Client(http=my_http, proxy="http://proxy")
```

### Back

Ownership is ambiguous: which object configures transport behavior? Reject conflicting inputs and make the injected transport authoritative.

```python
def __init__(self, http: "Http | None" = None, proxy: str | None = None):
    if http is not None and proxy is not None:
        raise ValueError("configure proxy on the injected HTTP client")
    self.http = http or DefaultHttp(proxy=proxy)
```

**Application:** Clear ownership also determines who closes connection pools.

**When not to use:** Do not create a custom transport protocol if injecting the vendor or `httpx` client directly suffices.

**Card ID:** C016
**Tags:** dependency-injection, http, configuration, resource-lifecycle
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `stripe/stripe-python` at commit `07b9a74cf02ce55413237a434be807190fccc3a7`
**Source example:** [`stripe/_stripe_client.py` — `StripeClient.__init__`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/stripe/_stripe_client.py#L136-L195)

---CARD---

### Front

A deployment creation request times out. May the package retry it automatically?

```python
response = http.post("/deployments", json=payload)
```

### Back

Only after establishing duplicate-effect safety. The server may have created the deployment before the client timed out. Use a provider-supported idempotency key or reconcile by a stable request ID.

```python
from uuid import uuid4

request_id = str(uuid4())
http.post(
    "/deployments",
    json=payload,
    headers={"Idempotency-Key": request_id},
)
```

**Application:** Reads are often safer to retry than writes, but even reads need bounded budgets. Check the external service’s actual semantics.

**When not to use:** Never invent a client-side key if the service does not honor it.

**Card ID:** C017
**Tags:** retries, idempotency, writes, external-services
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `stripe/stripe-python` at commit `07b9a74cf02ce55413237a434be807190fccc3a7`
**Source example:** [`stripe/_api_requestor.py` — idempotency header construction](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/stripe/_api_requestor.py#L552-L574)
**Related test:** [`tests/test_api_requestor.py` — `test_uses_given_idempotency_key`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/tests/test_api_requestor.py#L827-L843)

---CARD---

### Front

Why is “retry every 5xx three times” an incomplete policy?

```python
if response.status >= 500:
    retry()
```

### Back

A policy must classify transport failures and responses, honor server direction such as `Retry-After`, enforce an overall budget, back off with jitter, and consider operation idempotency.

```python
def retryable(status: int, attempt: int, limit: int) -> bool:
    return attempt < limit and status in {408, 409, 429, 500, 502, 503, 504}
```

**Application:** Prefer the established client library’s retries; package-level retries should cover a higher-level operation only when semantics differ.

**When not to use:** Avoid stacked vendor, HTTP, and package retry loops that multiply attempts and latency.

**Card ID:** C018
**Tags:** retries, backoff, transient-failures, retry-budget
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `stripe/stripe-python` at commit `07b9a74cf02ce55413237a434be807190fccc3a7`
**Source example:** [`stripe/_http_client.py` — `HTTPClient._should_retry`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/stripe/_http_client.py#L117-L180)
**Related test:** [`tests/test_http_client.py` — `test_should_retry_on_codes`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/tests/test_http_client.py#L201-L238)

---CARD---

### Front

Why return an iterator for a remote artifact listing?

```python
def list_artifacts() -> list[Artifact]:
    return fetch_every_page()
```

### Back

An iterator defers I/O, limits memory, and lets callers stop early. Document that advancing it may perform network requests.

```python
from collections.abc import Iterator

def artifacts(client: "Client") -> Iterator["Artifact"]:
    cursor: str | None = None
    while True:
        page = client.page(cursor)
        yield from page.items
        cursor = page.next_cursor
        if cursor is None:
            return
```

**Application:** Use this for models, runs, objects, or files; test two pages and early termination.

**When not to use:** Return a list when results are guaranteed tiny and eager validation is more useful.

**Card ID:** C019
**Tags:** iterators, generators, pagination, lazy-evaluation
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `stripe/stripe-python` at commit `07b9a74cf02ce55413237a434be807190fccc3a7`
**Source example:** [`stripe/_list_object.py` — `ListObject.auto_paging_iter`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/stripe/_list_object.py#L100-L142)
**Related test:** [`tests/api_resources/test_list_object.py` — `test_iter_two_pages`](https://github.com/stripe/stripe-python/blob/07b9a74cf02ce55413237a434be807190fccc3a7/tests/api_resources/test_list_object.py#L275-L298)

---CARD---

### Front

What does genuine sync/async API parity require?

```python
def deploy_async() -> Result:
    return asyncio.run(deploy())
```

### Back

Parity means native sync and async transports, matching configuration and exceptions, correct cleanup, and equivalent tests. Calling `asyncio.run` inside library code breaks when a loop is already running.

```python
class Client:
    def close(self) -> None: ...

class AsyncClient:
    async def aclose(self) -> None: ...
```

**Application:** Provide both only if real callers need both; keep semantics aligned even though implementations differ.

**When not to use:** A sync-only package is better than an untested async facade.

**Card ID:** C020
**Tags:** async, sync-async-parity, clients, resource-lifecycle
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `openai/openai-python` at commit `cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f`
**Source example:** [`src/openai/_client.py` — `OpenAI.__init__`](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/src/openai/_client.py#L108-L168)

---CARD---

### Front

How are timeout and retry configuration different?

```python
Client(timeout=10, retries=3)
```

### Back

A per-attempt timeout bounds one network attempt. A retry policy decides whether and when another attempt happens. Three ten-second attempts plus backoff can exceed thirty seconds, so important operations also need an overall deadline.

```python
from time import monotonic

deadline = monotonic() + 20
for attempt in range(3):
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise TimeoutError("operation deadline exceeded")
    call(timeout=min(5, remaining))
```

**Application:** Expose these controls separately and document whether timeout is per request or whole operation.

**When not to use:** Do not add a second retry layer merely to create an overall timeout; use a deadline around the native client.

**Card ID:** C021
**Tags:** timeouts, retries, deadlines, external-services
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `openai/openai-python` at commit `cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f`
**Source example:** [`src/openai/_base_client.py` — `_calculate_retry_timeout()`](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/src/openai/_base_client.py#L797-L858)

---CARD---

### Front

Why add jitter to exponential backoff?

```python
delay = 2 ** attempt
```

### Back

Without jitter, many clients that fail together retry together, creating synchronized load. Randomization spreads retries while a cap prevents absurd waits.

```python
import random

def delay(attempt: int) -> float:
    base = min(0.5 * 2 ** attempt, 8.0)
    return base * random.uniform(0.75, 1.0)
```

**Application:** Honor a bounded server `Retry-After` when valid; inject randomness and sleep for deterministic tests.

**When not to use:** Immediate local retries for lock-free pure computation gain nothing from network-style backoff.

**Card ID:** C022
**Tags:** retries, backoff, jitter, testability
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `openai/openai-python` at commit `cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f`
**Source example:** [`src/openai/_base_client.py` — retry calculation](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/src/openai/_base_client.py#L797-L858)
**Related test:** [`tests/test_client.py` — `test_does_not_retry_retry_after_above_max`](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/tests/test_client.py#L1128-L1142)

---CARD---

### Front

What should a stable connection-error hierarchy let callers express?

```python
try:
    call_service()
except Exception:
    print("service failed")
```

### Back

Callers should catch broadly when recovery is shared or narrowly when it differs. Timeout can be a connection-error subtype; status errors can retain safe response and request-ID metadata.

```python
class ServiceError(Exception): pass
class ConnectionError(ServiceError): pass
class RequestTimeout(ConnectionError): pass
class ResponseError(ServiceError):
    def __init__(self, status: int, request_id: str | None):
        self.status, self.request_id = status, request_id
```

**Application:** The CLI can map stable categories to exit codes; services can retry only transient categories.

**When not to use:** Avoid subclasses that callers handle identically.

**Card ID:** C023
**Tags:** exception-hierarchies, error-translation, public-api, timeouts
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `openai/openai-python` at commit `cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f`
**Source example:** [`src/openai/_exceptions.py` — API exception hierarchy](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/src/openai/_exceptions.py#L36-L114)
**Related test:** [`tests/test_client.py` — `test_request_timeout`](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/tests/test_client.py#L336-L343)

---CARD---

### Front

How should a large SDK contain generated endpoint and schema code?

```python
from package.generated.everything import *
```

### Back

Keep generated models/resources separate from handwritten auth, transport, retries, errors, and the public facade. Generation can then change repetitive code without obscuring infrastructure ownership.

```python
# public.py: stable handwritten facade
from ._client import Client
from .generated.models import Deployment

__all__ = ["Client", "Deployment"]
```

**Application:** An internal package should usually handwrite a small typed model set; code generation pays off only for a large changing specification.

**When not to use:** Do not reproduce enterprise SDK folder depth around five operations.

**Card ID:** C024
**Tags:** generated-code, public-api, import-boundaries, overengineering
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `openai/openai-python` at commit `cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f`
**Source example:** [`src/openai/pagination.py` — generated pagination surface](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/src/openai/pagination.py#L1-L68)

---CARD---

### Front

How should resource ownership work when a client accepts an injected transport?

```python
with ServiceClient(http=shared_http) as client:
    client.call()
```

### Back

The API must document whether closing the service client closes the injected transport. A safe common rule is: the creator owns and closes injected resources; the service client closes only transports it created.

```python
class ServiceClient:
    def __init__(self, http: "Http | None" = None) -> None:
        self._owns_http = http is None
        self._http = http or Http()

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
```

**Application:** This prevents leaked pools and accidental closure of a process-wide shared client.

**When not to use:** If ownership is always transferred, state that clearly and keep the implementation simpler.

**Card ID:** C025
**Tags:** resource-lifecycle, dependency-injection, clients, cleanup
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `openai/openai-python` at commit `cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f`
**Source example:** [`src/openai/_base_client.py` — `SyncAPIClient.__init__`](https://github.com/openai/openai-python/blob/cbdc98b6c1e21df7ee43d13b5de7243c6ed1ee7f/src/openai/_base_client.py#L900-L954)

---CARD---

### Front

What bug occurs if mutable class metadata is inherited directly by every workflow subclass?

```python
class Base:
    plugins: list[str] = []

class Train(Base): pass
class Deploy(Base): pass
Train.plugins.append("gpu")
```

### Back

`Train.plugins` and `Deploy.plugins` refer to the same list, so configuring one workflow contaminates another. Initialize new state for each subclass, then deliberately merge inherited values.

```python
class Base:
    plugins: list[str]

    def __init_subclass__(cls) -> None:
        inherited = getattr(cls, "plugins", ())
        cls.plugins = list(inherited)
```

**Application:** Per-class state matters for workflow definitions, provider registrations, and test fixtures. Make ownership and inheritance rules explicit.

**When not to use:** Prefer instance state when metadata does not need to exist before construction.

**Card ID:** C002
**Tags:** class-state, inheritance, init-subclass, mutability
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `Netflix/metaflow` at commit `3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4`
**Source example:** [`metaflow/flowspec.py` — `FlowSpecMeta._init_attrs()`](https://github.com/Netflix/metaflow/blob/3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4/metaflow/flowspec.py#L174-L257)

---CARD---

### Front

Why should a decorator preserve a function's signature and metadata?

```python
def traced(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

### Back

Without `functools.wraps`, introspection sees `wrapper`, documentation loses the original name, and frameworks that inspect parameters may behave incorrectly. Static typing should also preserve the callable signature.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def traced(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)
    return wrapper
```

**Application:** Preserve signatures on decorators used for Click helpers, retries, logging, and workflow steps.

**When not to use:** A plain higher-order function is enough when returning a genuinely different interface.

**Card ID:** C003
**Tags:** decorators, paramspec, callable, signature-preservation
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `Netflix/metaflow` at commit `3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4`
**Source example:** [`metaflow/decorators.py` — `step()` overloads](https://github.com/Netflix/metaflow/blob/3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4/metaflow/decorators.py#L1099-L1165)

---CARD---

### Front

What do overloads contribute when a decorator accepts more than one valid function shape?

```python
from collections.abc import Callable

def step(fn: Callable[..., None]) -> Callable[..., None]:
    fn.is_step = True  # type: ignore[attr-defined]
    return fn
```

### Back

Overloads describe distinct caller-visible relationships that a broad implementation annotation cannot express. They help a checker preserve accepted arguments and reject invalid decorator ordering or shapes; they do not create runtime dispatch.

```python
from typing import overload

@overload
def normalize(value: str) -> str: ...
@overload
def normalize(value: list[str]) -> list[str]: ...

def normalize(value: str | list[str]) -> str | list[str]:
    return value.strip() if isinstance(value, str) else [v.strip() for v in value]
```

**Application:** Use overloads for public APIs whose return type depends on an input type, including sync helpers and decorator forms.

**When not to use:** A union is clearer when callers gain no more precise result type.

**Card ID:** C004
**Tags:** typing, overloads, decorators, type-narrowing
**Difficulty:** Advanced
**Source type:** Repository
**Source:** `Netflix/metaflow` at commit `3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4`
**Source example:** [`metaflow/decorators.py` — `step()`](https://github.com/Netflix/metaflow/blob/3d6fa45348329af8f21fdd1dd7dc13666d7c8ff4/metaflow/decorators.py#L1099-L1127)

---CARD---

### Front

Your package supports `file://`, `gs://`, and `s3://` artifacts. Where should URI selection live?

```python
def download(uri: str) -> bytes:
    if uri.startswith("gs://"): ...
    elif uri.startswith("s3://"): ...
    else: ...
```

### Back

Put selection in a small registry/factory and behavior behind a common interface. Callers depend on one abstraction, while each adapter owns provider-specific authentication and I/O.

```python
from collections.abc import Callable
from typing import Protocol

class Store(Protocol):
    def read(self, uri: str) -> bytes: ...

factories: dict[str, Callable[[], Store]] = {}

def store_for(uri: str) -> Store:
    scheme = uri.partition(":")[0] or "file"
    try:
        return factories[scheme]()
    except KeyError as exc:
        raise ValueError(f"unsupported artifact scheme: {scheme}") from exc
```

**Application:** A GCS adapter and local fake can share the same artifact service without conditionals spreading through the package.

**When not to use:** Two fixed implementations can be injected directly; plugin discovery is unnecessary.

**Card ID:** C005
**Tags:** mlflow, factories, registries, adapters, protocol
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/store/artifact/artifact_repository_registry.py` — `ArtifactRepositoryRegistry`](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/store/artifact/artifact_repository_registry.py#L26-L93)

---CARD---

### Front

When is a dictionary registry preferable to a full plugin system?

```python
STORES = {"file": LocalStore, "gs": GcsStore}
```

### Back

A dictionary is explicit, debuggable, typed, and sufficient when the package controls all implementations. Entry-point discovery is justified when independently distributed packages must add implementations without changing the core package.

```python
def register_store(scheme: str, factory: type[Store]) -> None:
    if scheme in STORES:
        raise ValueError(f"duplicate store: {scheme}")
    STORES[scheme] = factory
```

**Application:** Start with an internal registry for GCP and local storage. Add packaging entry points only after third-party extension is a real requirement.

**When not to use:** Direct dependency injection is simplest when each command uses one known client.

**Card ID:** C006
**Tags:** plugins, registries, dependency-injection, overengineering
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/store/artifact/artifact_repository_registry.py` — `register_entrypoints()`](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/store/artifact/artifact_repository_registry.py#L39-L57)

---CARD---

### Front

Why is a context manager a strong API for an experiment run lifecycle?

```python
run = client.start_run()
train()
client.end_run(run)
```

### Back

The manual form leaks an active run if `train()` raises. A context manager centralizes success/failure status and cleanup in `__exit__`, while still allowing an explicit lifecycle when needed.

```python
from contextlib import contextmanager
from collections.abc import Iterator

@contextmanager
def run(client: "Client") -> Iterator[str]:
    run_id = client.start()
    try:
        yield run_id
    except Exception:
        client.end(run_id, status="FAILED")
        raise
    else:
        client.end(run_id, status="FINISHED")
```

**Application:** Use this for MLflow runs, temporary credentials, files, sessions, and deployment leases.

**When not to use:** A one-shot stateless call needs no lifecycle abstraction.

**Card ID:** C007
**Tags:** mlflow, context-managers, cleanup, resource-lifecycle
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/tracking/fluent.py` — `start_run()`](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/tracking/fluent.py#L450-L504)

---CARD---

### Front

What configuration precedence should an API use when both an explicit argument and environment variable can select a run?

```python
run_id = os.getenv("RUN_ID") or supplied_run_id
```

### Back

Explicit caller input should normally win, followed by environment/config-file values, then defaults. Reversing the order makes invisible process state override deliberate code.

```python
import os

def resolve_run_id(supplied: str | None) -> str | None:
    if supplied is not None:
        return supplied
    return os.getenv("RUN_ID")
```

Document precedence as part of the public contract and test every branch, including empty and malformed values.

**Application:** Apply one consistent order to GCP project, MLflow tracking URI, region, timeouts, and credentials—while respecting provider-native authentication chains.

**When not to use:** Do not add environment-variable support to a value that must always be explicit for safety.

**Card ID:** C008
**Tags:** configuration, environment-variables, precedence, authentication
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/tracking/fluent.py` — `start_run()` precedence](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/tracking/fluent.py#L450-L484)

---CARD---

### Front

Why should a package define domain exceptions instead of exposing raw HTTP or cloud-client errors everywhere?

```python
def deploy() -> None:
    cloud.create_job()  # may raise many vendor exceptions
```

### Back

A package-owned hierarchy gives library callers a stable contract while adapters translate changing vendor errors. Preserve the original cause with `raise ... from ...`.

```python
class PackageError(Exception): pass
class AuthenticationError(PackageError): pass
class TransientServiceError(PackageError): pass

def deploy() -> None:
    try:
        cloud.create_job()
    except VendorUnauthenticated as exc:
        raise AuthenticationError("cloud authentication failed") from exc
```

**Application:** The CLI can map `AuthenticationError` to concise stderr and an exit code, while library users can catch it without importing a vendor SDK.

**When not to use:** Do not wrap every programming error; preserve unexpected failures and tracebacks.

**Card ID:** C009
**Tags:** exceptions, exception-translation, exception-chaining, public-api
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/exceptions.py` — `MlflowException`](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/exceptions.py#L68-L130)

---CARD---

### Front

What is dangerous about putting sensitive vendor response text into a user-facing exception?

```python
try:
    call_service()
except HttpError as exc:
    raise PackageError(str(exc)) from exc
```

### Back

The response may contain tokens, signed URLs, request bodies, or internal identifiers. Separate a safe public message from diagnostic details, and redact structured logs.

```python
try:
    call_service()
except HttpError as exc:
    logger.warning(
        "deployment_failed",
        status=exc.status,
        request_id=exc.request_id,
    )
    raise PackageError("deployment service rejected the request") from exc
```

**Application:** CLI output must be safe by default; authorized debugging can use controlled logs and cloud request IDs.

**When not to use:** Do not discard useful non-sensitive classifications such as status, retryability, or request ID.

**Card ID:** C010
**Tags:** exceptions, secrets, redaction, logging
**Difficulty:** Intermediate
**Source type:** Repository
**Source:** `mlflow/mlflow` at commit `8ab8acc1ca13995a1d1b37741f94f5a8881e30c2`
**Source example:** [`mlflow/exceptions.py` — `MlflowException` safety guidance](https://github.com/mlflow/mlflow/blob/8ab8acc1ca13995a1d1b37741f94f5a8881e30c2/mlflow/exceptions.py#L68-L96)

---CARD---

### Front
When are class methods useful?

### Back

Class methods are useful as alternative constructors or when we want to express logic for getting class attributes wihout repeating the code for 
all the subclasses