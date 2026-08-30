# 1. Facade / Resource Pattern

## What it is

The **Facade pattern** gives users a simple, high-level interface over a more complicated system.

The **Resource pattern** organizes related operations into logical groups.

For an MLOps SDK, instead of users creating and managing a bunch of separate classes:

```python
experiment_service = ExperimentService(...)
bigquery_service = BigQueryService(...)
pipeline_service = PipelineService(...)
```

you give them one main entry point:

```python
mlops = MLOpsClient()

mlops.mlflow.create_experiment(...)
mlops.bigquery.query(...)
mlops.pipelines.create(...)
```

The `MLOpsClient` is the **facade**.

`mlflow`, `bigquery`, and `pipelines` are **resources/services** exposed through that facade.

## Why it's useful

It makes the SDK:

* easier to discover
* easier to document
* easier to use
* easier to organize internally

Users only need to remember one main object:

```python
MLOpsClient
```

and then explore its resources.

## Simple example

```python
class MLflowResource:
    """Provides MLflow-related operations."""

    def create_experiment(self, name: str) -> None:
        """Create a new MLflow experiment.

        Args:
            name: Name of the experiment.
        """
        print(f"Creating MLflow experiment: {name}")


class BigQueryResource:
    """Provides BigQuery-related operations."""

    def query(self, sql: str) -> None:
        """Execute a BigQuery SQL query.

        Args:
            sql: SQL statement to execute.
        """
        print(f"Running BigQuery query: {sql}")


class MLOpsClient:
    """Main entry point for the MLOps SDK.

    The client acts as a facade over the different MLOps
    resources exposed by the SDK.
    """

    def __init__(self) -> None:
        """Initialize the SDK resources."""
        self.mlflow = MLflowResource()
        self.bigquery = BigQueryResource()
```

Usage:

```python
mlops = MLOpsClient()

mlops.mlflow.create_experiment("fraud-model")

mlops.bigquery.query(
    "SELECT * FROM project.dataset.features"
)
```

The user doesn't need to know how the internal services are constructed.

## How this might look in your real SDK

```text
MLOpsClient
│
├── mlflow
│   ├── experiments
│   ├── runs
│   └── models
│
├── bigquery
│
├── storage
│
├── pipelines
│
└── repos
```

Usage might become:

```python
mlops.mlflow.experiments.get_or_create("fraud")

mlops.mlflow.models.promote("fraud-model", "uat")

mlops.bigquery.load_dataframe(df, table)

mlops.pipelines.scaffold("training")

mlops.repos.scaffold("fraud-model")
```

This is probably the **first architectural pattern I would establish**.

---

# 2. Dependency Injection

## What it is

**Dependency Injection** means a class receives the objects it depends on instead of creating them internally.

Suppose your BigQuery wrapper needs Google's `bigquery.Client`.

A tightly coupled implementation would be:

```python
from google.cloud import bigquery


class BigQueryService:
    """BigQuery operations used by the SDK."""

    def __init__(self) -> None:
        """Create the Google BigQuery client."""
        self._client = bigquery.Client()
```

The problem is that `BigQueryService` now decides:

> "I will create my own BigQuery client."

That makes testing and configuration harder.

With dependency injection:

```python
class BigQueryService:
    """BigQuery operations used by the SDK."""

    def __init__(self, client) -> None:
        """Initialize the service.

        Args:
            client: BigQuery-compatible client used to execute queries.
        """
        self._client = client
```

Now somebody else provides the dependency.

## Why it's useful

This is especially important for your SDK because you'll depend on many external systems:

```text
MLflow
BigQuery
GCS
Vertex AI
Secret Manager
Git
filesystem
subprocess
HTTP
```

Dependency injection makes them:

* replaceable
* configurable
* testable
* loosely coupled

## Simple example

```python
class BigQueryService:
    """Service responsible for BigQuery operations."""

    def __init__(self, client) -> None:
        """Initialize the service.

        Args:
            client: Object capable of executing BigQuery queries.
        """
        self._client = client

    def query(self, sql: str):
        """Execute a SQL query.

        Args:
            sql: SQL statement to execute.

        Returns:
            Query results returned by the underlying client.
        """
        return self._client.query(sql)
```

Production code:

```python
from google.cloud import bigquery


google_client = bigquery.Client()

service = BigQueryService(
    client=google_client
)
```

But during testing:

```python
class FakeBigQueryClient:
    """Fake BigQuery client used by unit tests."""

    def query(self, sql: str) -> list[dict]:
        """Return fake query results.

        Args:
            sql: SQL statement that would have been executed.

        Returns:
            Fake rows for testing.
        """
        return [
            {"user_id": 1},
            {"user_id": 2},
        ]


fake_client = FakeBigQueryClient()

service = BigQueryService(
    client=fake_client
)

rows = service.query(
    "SELECT * FROM users"
)
```

No real BigQuery call happens.

## The core idea

Without dependency injection:

```text
BigQueryService
     │
     ▼
creates BigQuery client itself
```

With dependency injection:

```text
MLOpsClient
     │
     ├── creates/configures BigQuery client
     │
     ▼
BigQueryService
     │
     ▼
uses provided client
```

The service focuses on **BigQuery behavior**, not figuring out how to construct its dependencies.

---

# 3. Adapter Pattern

## What it is

The **Adapter pattern** converts one interface or data representation into another one that your application prefers.

Your SDK will interact with APIs such as:

```text
MLflow
BigQuery
Vertex AI
GCS
```

Those libraries have their own objects and interfaces.

Instead of allowing those external types to spread throughout your SDK, an adapter can translate them into your own representation.

## Example problem

Suppose MLflow returns something like:

```python
MlflowRun(
    info=RunInfo(
        run_id="abc123",
        experiment_id="42",
        status="FINISHED",
    )
)
```

You don't necessarily want everyone using your SDK to know about:

```python
run.info.run_id
```

Maybe your SDK wants a simpler representation:

```python
Run(
    id="abc123",
    experiment_id="42",
    status="FINISHED",
)
```

An adapter performs that conversion.

## Simple example

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Run:
    """SDK representation of an MLflow run.

    Attributes:
        id: Unique run identifier.
        experiment_id: Experiment containing the run.
        status: Current run status.
    """

    id: str
    experiment_id: str
    status: str


def adapt_mlflow_run(mlflow_run) -> Run:
    """Convert an MLflow run into the SDK's Run model.

    Args:
        mlflow_run: Run object returned by MLflow.

    Returns:
        SDK-native Run object.
    """
    return Run(
        id=mlflow_run.info.run_id,
        experiment_id=mlflow_run.info.experiment_id,
        status=mlflow_run.info.status,
    )
```

Then your service might do:

```python
class RunService:
    """Provides run-related MLflow operations."""

    def __init__(self, mlflow_client) -> None:
        """Initialize the service.

        Args:
            mlflow_client: MLflow client used to retrieve runs.
        """
        self._client = mlflow_client

    def get(self, run_id: str) -> Run:
        """Retrieve an MLflow run.

        Args:
            run_id: Unique MLflow run identifier.

        Returns:
            SDK-native representation of the run.
        """
        raw_run = self._client.get_run(run_id)

        return adapt_mlflow_run(raw_run)
```

Now your user gets:

```python
run = mlops.mlflow.runs.get("abc123")

print(run.id)
print(run.status)
```

instead of:

```python
run.info.run_id
run.info.status
```

## Why it's useful

Imagine MLflow changes something internally.

Without an adapter:

```text
MLflow object
     ↓
service A
     ↓
service B
     ↓
your application
     ↓
tests
```

Everyone may depend on MLflow's representation.

With an adapter:

```text
MLflow
   │
   ▼
Adapter
   │
   ▼
Your SDK model
   │
   ├── SDK code
   ├── user code
   └── tests
```

If MLflow changes, ideally you only modify the adapter.

## Another example: BigQuery

External object:

```python
google.cloud.bigquery.table.Row
```

Your SDK might convert it to:

```python
@dataclass(frozen=True)
class DatasetInfo:
    """Metadata describing a BigQuery dataset."""

    project: str
    dataset: str
    location: str
```

This keeps Google's object model from leaking everywhere.

---

# 4. Factory Pattern

## What it is

A **Factory** is responsible for creating an object.

In Python SDKs, one very common form of the Factory pattern is an **alternate constructor using `@classmethod`**.

Instead of requiring the user to know exactly how to create everything:

```python
client = MLOpsClient(
    project_id=os.environ["PROJECT_ID"],
    region=os.environ["REGION"],
    mlflow_uri=os.environ["MLFLOW_URI"],
)
```

you can offer:

```python
client = MLOpsClient.from_env()
```

The factory handles the construction logic.

## Simple example

```python
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MLOpsConfig:
    """Configuration required by the MLOps SDK.

    Attributes:
        project_id: Google Cloud project ID.
        region: Default Google Cloud region.
        mlflow_uri: URI of the MLflow tracking server.
    """

    project_id: str
    region: str
    mlflow_uri: str


class MLOpsClient:
    """Top-level client for the MLOps SDK."""

    def __init__(self, config: MLOpsConfig) -> None:
        """Initialize the client.

        Args:
            config: SDK configuration.
        """
        self.config = config

    @classmethod
    def from_env(cls) -> "MLOpsClient":
        """Create an MLOps client from environment variables.

        Expected environment variables:
            GCP_PROJECT_ID
            GCP_REGION
            MLFLOW_TRACKING_URI

        Returns:
            Configured MLOpsClient instance.
        """
        config = MLOpsConfig(
            project_id=os.environ["GCP_PROJECT_ID"],
            region=os.environ["GCP_REGION"],
            mlflow_uri=os.environ["MLFLOW_TRACKING_URI"],
        )

        return cls(config)
```

Usage:

```python
mlops = MLOpsClient.from_env()
```

The important part is:

```python
return cls(config)
```

The classmethod's job is to figure out **how to construct the object**.

## You might eventually support several factories

```python
MLOpsClient.from_env()

MLOpsClient.from_yaml("mlops.yaml")

MLOpsClient.for_project("my-project")

MLOpsClient.for_environment("dev")
```

For example:

```python
class MLOpsClient:
    """Top-level MLOps SDK client."""

    @classmethod
    def for_environment(cls, environment: str) -> "MLOpsClient":
        """Create a client configured for a deployment environment.

        Args:
            environment: Environment name such as "dev", "uat", or "prod".

        Returns:
            Configured MLOpsClient instance.

        Raises:
            ValueError: If the environment is unsupported.
        """
        projects = {
            "dev": "company-ml-dev",
            "uat": "company-ml-uat",
            "prod": "company-ml-prod",
        }

        if environment not in projects:
            raise ValueError(
                f"Unknown environment: {environment}"
            )

        config = MLOpsConfig(
            project_id=projects[environment],
            region="us-central1",
            mlflow_uri=f"https://mlflow-{environment}.company.com",
        )

        return cls(config)
```

Usage:

```python
mlops = MLOpsClient.for_environment("dev")
```

## Why it's useful

The caller says:

> "Give me a client configured for dev."

The factory figures out:

> "What does dev actually mean?"

That's exactly the kind of company-specific knowledge your internal SDK can encapsulate.

---

# 5. Protocol / Strategy Pattern

These are technically two related concepts, but they work extremely well together.

## Protocol: what behavior must exist?

A `Protocol` defines an interface.

For example:

> Anything that wants to execute a pipeline must provide a `run()` method.

```python
from typing import Protocol


class PipelineExecutor(Protocol):
    """Interface implemented by pipeline execution backends."""

    def run(self, pipeline_name: str) -> str:
        """Execute a pipeline.

        Args:
            pipeline_name: Name of the pipeline to execute.

        Returns:
            Identifier of the created pipeline run.
        """
        ...
```

Notice that the Protocol does not actually execute anything.

It just defines the contract:

```text
A PipelineExecutor must have:

run(pipeline_name) -> str
```

---

## Strategy: different implementations of the behavior

The **Strategy pattern** says that an algorithm or behavior can have multiple interchangeable implementations.

For your SDK, pipeline execution might happen:

```text
locally
Vertex AI
Cloud Composer
```

All three are different strategies.

### Local strategy

```python
class LocalPipelineExecutor:
    """Executes pipelines on the local machine."""

    def run(self, pipeline_name: str) -> str:
        """Run a pipeline locally.

        Args:
            pipeline_name: Name of the pipeline to execute.

        Returns:
            Identifier for the local pipeline run.
        """
        print(f"Running {pipeline_name} locally")

        return "local-run-123"
```

### Vertex AI strategy

```python
class VertexPipelineExecutor:
    """Executes pipelines using Vertex AI Pipelines."""

    def __init__(self, vertex_client) -> None:
        """Initialize the executor.

        Args:
            vertex_client: Client used to communicate with Vertex AI.
        """
        self._client = vertex_client

    def run(self, pipeline_name: str) -> str:
        """Submit a pipeline to Vertex AI.

        Args:
            pipeline_name: Name of the pipeline to execute.

        Returns:
            Vertex AI pipeline job identifier.
        """
        print(
            f"Submitting {pipeline_name} to Vertex AI"
        )

        return "vertex-job-456"
```

Both satisfy:

```python
PipelineExecutor
```

Now your pipeline service can accept either one.

```python
class PipelineService:
    """Coordinates pipeline operations."""

    def __init__(self, executor: PipelineExecutor) -> None:
        """Initialize the pipeline service.

        Args:
            executor: Strategy used to execute pipelines.
        """
        self._executor = executor

    def run(self, pipeline_name: str) -> str:
        """Execute a pipeline using the configured strategy.

        Args:
            pipeline_name: Name of the pipeline.

        Returns:
            Pipeline run identifier.
        """
        return self._executor.run(pipeline_name)
```

Usage with local execution:

```python
service = PipelineService(
    executor=LocalPipelineExecutor()
)

service.run("training-pipeline")
```

Later:

```python
service = PipelineService(
    executor=VertexPipelineExecutor(vertex_client)
)

service.run("training-pipeline")
```

`PipelineService` doesn't change.

That's the important part.

## Without Strategy

You often end up with code like:

```python
def run_pipeline(name: str, backend: str):
    """Run a pipeline against the requested backend."""

    if backend == "local":
        ...
    elif backend == "vertex":
        ...
    elif backend == "composer":
        ...
    elif backend == "something_else":
        ...
```

As more backends appear, this gets increasingly messy.

## With Strategy

You get:

```text
                  PipelineExecutor
                        ▲
              ┌─────────┼─────────┐
              │         │         │
            Local     Vertex    Composer
```

And the calling code only knows:

```python
executor.run(...)
```

## Why Protocol is especially nice in Python

You don't even have to explicitly inherit from the Protocol.

This works:

```python
class LocalPipelineExecutor:
    """Executes pipelines locally."""

    def run(self, pipeline_name: str) -> str:
        """Run the requested pipeline."""
        return "123"
```

Python's typing system recognizes:

> It has the required `run()` method, therefore it satisfies `PipelineExecutor`.

This is called **structural typing**.

Think:

> "If it walks like a duck and quacks like a duck, treat it like a duck."

That's very useful for SDK design.

---

# Putting All 5 Together

These patterns complement each other.

Imagine your SDK starts here:

```python
mlops = MLOpsClient.from_env()

mlops.bigquery.query(...)

mlops.mlflow.experiments.get_or_create(...)

mlops.pipelines.run(...)
```

Underneath, you could have:

```text
                    MLOpsClient
                       │
                       │ Facade
                       ▼
         ┌─────────────┼──────────────┐
         │             │              │
      MLflow        BigQuery      Pipelines
      Resource       Resource       Resource
         │             │              │
         │             │              ▼
         │             │       PipelineExecutor
         │             │              ▲
         │             │         Strategy/Protocol
         │             │       ┌──────┴───────┐
         │             │       │              │
         │             │     Local          Vertex
         │             │
         ▼             ▼
      Adapter        Adapter
         │             │
         ▼             ▼
     MLflow SDK     Google SDK


External clients are passed in through
Dependency Injection.


MLOpsClient.from_env()
        ▲
        │
      Factory
```

So each pattern is solving a different problem.

| Pattern                  | Main question it answers                                                         |
| ------------------------ | -------------------------------------------------------------------------------- |
| **Facade / Resource**    | How should users navigate my SDK?                                                |
| **Dependency Injection** | How should classes receive the things they depend on?                            |
| **Adapter**              | How do I isolate my SDK from MLflow/GCP-specific representations?                |
| **Factory**              | How should complicated objects/configurations be created?                        |
| **Protocol / Strategy**  | How do I support interchangeable implementations without giant `if/elif` blocks? |

If I were building your MLOps SDK from scratch, **Facade/Resource + Dependency Injection would be the foundation**, and then Adapter, Factory, and Protocol/Strategy would naturally appear as the SDK grows.
