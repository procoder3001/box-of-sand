# Build a small MLOps SDK: a guided course

This course is a cumulative build of one deliberately small SDK. It follows the architecture in [`notes.md`](../notes.md): a boring public facade, resource-oriented services, injected third-party clients, adapters at external boundaries, and strategies only where behavior genuinely varies.

This is not intended to become your production SDK. It is a rehearsal: after completing it, the roles and locations of the important files should feel familiar.

## What you will build

```text
consumer / CLI
      |
      v
MLOpsClient                 public facade
  |-- mlflow                resource/service
  |     |-- experiments
  |     `-- run(...)        context-managed lifecycle
  |-- pipelines             builder + execution strategy
        |
        `-- PipelineExecutor protocol
  `-- etl                   feature plan + execution strategy
        |-- SparkExecutor → injected Spark gateway
        `-- BeamExecutor  → injected Beam gateway

External MLflow-shaped object
      |
      v
MLflowAdapter               translation and error boundary
      |
      v
Run                         package-owned frozen dataclass
```

The final project layout is:

```text
src/company_mlops/
├── __init__.py             deliberately small public API
├── config.py               trusted immutable configuration
├── models.py               package-owned values + Pydantic wire model
├── ports.py                Protocols for injected dependencies
├── errors.py               package-owned exception hierarchy
├── adapters/mlflow.py      third-party shapes → package shapes
├── services/mlflow.py      use cases and run lifecycle
├── pipelines.py            spec, builder, and execution strategies
├── etl/                    feature plans and Spark/Beam executor adapters
├── client.py               facade and dependency wiring
└── cli.py                  thin command adapter
```

## How to use the course

Use Python 3.12+ in a virtual environment. From `guided_mlops_sdk/learner`:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q tests/test_01_config_and_models.py
```

Then follow the guides in order. Only edit `learner/src/company_mlops/`. Each guide names the exact test to run. The learner package contains signatures and documentation but leaves the decisions and implementation to you.

The complete project is under `solution/`. Compare only after your relevant test passes or you have written down exactly where you are stuck:

```bash
cd ../solution
python -m pip install -e '.[dev]'
pytest -q
```

## Lesson map

| Lesson | Guide | Primary files | Main decision |
|---|---|---|---|
| 1 | [Configuration and models](guides/01_configuration_and_models.md) | `config.py`, `models.py` | dataclass vs Pydantic; classmethod as alternate constructor |
| 2 | [Ports, adapters, and DI](guides/02_ports_adapters_and_di.md) | `ports.py`, `adapters/mlflow.py` | Protocol vs ABC; isolate third-party objects |
| 3 | [Services and facade](guides/03_services_and_facade.md) | `services/mlflow.py`, `client.py` | resource API, injected dependencies, lazy properties |
| 4 | [Lifecycles and errors](guides/04_lifecycles_and_errors.md) | `errors.py`, `services/mlflow.py` | context managers, cleanup, exception translation |
| 5 | [Pipeline construction](guides/05_pipeline_builder_and_strategy.md) | `pipelines.py` | modern generics, strategy, selective builder use |
| 6 | [Async SDK operations](guides/06_async_operations.md) | `services/mlflow.py` | bounded concurrency, timeout, cancellation |
| 7 | [CLI and packaging](guides/07_cli_and_packaging.md) | `cli.py`, `__init__.py`, `pyproject.toml` | thin CLI and stable import surface |
| 8 | [ETL and feature engineering](guides/08_etl_and_feature_engineering.md) | `etl/`, `client.py` | portable plans vs Spark/Beam-specific execution |

## A decision checklist to reuse in your real SDK

Before adding a class, identify its job:

- Untrusted JSON/config input that needs parsing and detailed validation: Pydantic `BaseModel`.
- Trusted internal value with useful equality and representation: `dataclass`.
- Immutable identifier or specification: frozen dataclass, often with `slots=True`.
- A collaborator that merely needs certain methods: `Protocol`.
- An SDK-owned inheritance family sharing implementation or enforced invariants: ABC.
- Stateful orchestration or a public resource: ordinary class.
- Multiple named ways to construct the same valid object: `@classmethod` alternate constructors.
- Behavior selected at runtime: injected strategy, often described by a protocol.
- Many ordered/compositional construction steps: builder; otherwise prefer keyword arguments.

If you cannot state the job, start with a function or ordinary class. Advanced syntax is a tool, not an architectural goal.
