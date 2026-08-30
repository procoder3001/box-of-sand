# Lesson 8: ETL and feature engineering with Spark or Apache Beam

## What this lesson is trying to teach

Your SDK should help users describe and launch ETL work without becoming a homemade data-processing framework. Spark and Beam already own distributed execution, shuffles, serialization, retries, and worker lifecycle. Your package should own the stable workflow around them:

- validated dataset and feature specifications;
- naming and configuration conventions;
- selection and construction of an execution strategy;
- translation into provider-specific submissions;
- package-owned job results and errors;
- testable orchestration that does not start a cluster.

This follows the architecture from `notes.md`:

```text
MLOpsClient.etl
      |
      v
ETLService.materialize(plan, executor=...)
      |
      +-------------------+
      |                   |
      v                   v
SparkExecutor         BeamExecutor        strategy adapters
      |                   |
      v                   v
SparkGateway          BeamGateway         narrow injected boundaries
      |                   |
      v                   v
SparkSession          Beam runner         real framework, outside domain layer
```

The same immutable `FeaturePlan` enters either executor, but the compiled boundary is different. The SDK does not pretend Spark SQL expressions and Beam transforms are the same runtime abstraction.

## What you will build

The new package is:

```text
company_mlops/etl/
├── __init__.py       intentional ETL public imports
├── models.py         DatasetRef, FeatureSpec, MaterializationResult
├── plan.py           immutable FeaturePlan + mutable builder
├── executors.py      strategy protocol and Spark/Beam adapters
└── service.py        framework-neutral ETL use case
```

You will also add a lazy `client.etl` resource to the facade.

## Start with the public use case

The desired user code is deliberately boring:

```python
plan = (
    FeaturePlanBuilder(
        "training-features",
        source=DatasetRef("bq://project.raw.events"),
        destination=DatasetRef("bq://project.features.training"),
    )
    .add_feature(FeatureSpec.identity("country", "country_code"))
    .add_feature(FeatureSpec.ratio("click_rate", "clicks", "impressions"))
    .build()
)

result = client.etl.materialize(plan, executor=spark_executor)
```

Changing execution strategy should not change the plan or service call:

```python
result = client.etl.materialize(plan, executor=beam_executor)
```

This does not promise that every Spark transformation can run on Beam. It means the small portable feature vocabulary defined by this SDK has two compilers.

## Part 1: immutable ETL values

### Files to edit

Open `learner/src/company_mlops/etl/models.py`.

Implement these in order:

1. `DatasetRef.__post_init__`: reject an empty URI.
2. `FeatureSpec.__post_init__`: reject an empty name or input column.
3. Require one input for `IDENTITY` and two for `RATIO`.
4. Implement `FeatureSpec.identity` and `FeatureSpec.ratio` using `cls(...)`.

These are frozen dataclasses because they are trusted domain values after construction. Their equality makes plans and tests readable, and immutability prevents an executor from silently modifying the requested feature definition.

The alternate constructors communicate intent better than repeatedly exposing enum and tuple details:

```python
FeatureSpec.ratio("click_rate", "clicks", "impressions")
```

They use `cls`, so a specialized subclass can inherit them without receiving a base `FeatureSpec` accidentally.

### Why not Pydantic here?

These objects are constructed by typed Python library calls. A frozen dataclass plus small invariant checks is enough. If feature plans arrive from YAML, JSON, or a REST API, validate that untrusted input with a Pydantic boundary model and convert it to these values.

Do not make every internal value inherit from `BaseModel`. That couples domain code, equality, serialization, and public behavior to the validation framework when simple data semantics are sufficient.

## Part 2: build a complete feature plan

Open `etl/plan.py` and implement `FeaturePlanBuilder`:

1. Validate a non-empty plan name in `__init__`.
2. Keep an internal mutable list of features.
3. Reject duplicate feature output names in `add_feature`.
4. Return `self` for the fluent API.
5. Require at least one feature in `build`.
6. Convert the list to a tuple when constructing `FeaturePlan`.

The tuple is an important snapshot. This must remain true:

```python
first = builder.add_feature(country).build()
builder.add_feature(click_rate)
assert first.features == (country,)
```

### When is this builder justified?

It is useful because a feature plan is accumulated, ordered, and validated for completeness. If your actual job only has `source`, `destination`, and one transform, prefer direct `FeaturePlan(...)` construction. Do not add a builder purely because distributed-data libraries use fluent APIs.

## Part 3: define the variable behavior as a strategy

Read `ETLExecutor` in `etl/executors.py`:

```python
class ETLExecutor(Protocol):
    provider: str
    def execute(self, plan: FeaturePlan) -> MaterializationResult: ...
```

It is a protocol because callers may inject Spark, Beam, local, or recording implementations without inheriting from your package. `ETLService` only needs this capability.

Implement `ETLService.materialize` as a one-line delegation. Do not add:

```python
if engine == "spark": ...
elif engine == "beam": ...
```

Provider selection belongs at dependency wiring time. This keeps the service open to a local executor or future provider without editing its core branch logic.

## Part 4: compile for Spark

Implement `SparkExecutor` in `etl/executors.py`:

1. Store the injected `SparkGateway`.
2. Convert each identity feature to its source-column expression.
3. Convert a ratio to `(<numerator> / <denominator>)`.
4. Submit source, destination, and the output-name/expression mapping.
5. Return a package-owned `MaterializationResult` with provider `spark`.

The gateway is intentionally narrow. A production gateway might contain the only imports of `pyspark`:

```python
class PySparkGateway:
    def __init__(self, spark: SparkSession) -> None:
        self._spark = spark

    def submit_sql_features(self, *, source_uri, destination_uri, columns):
        frame = self._spark.read.format("bigquery").load(source_uri)
        for output_name, expression in columns.items():
            frame = frame.withColumn(output_name, expr(expression))
        frame.write.mode("overwrite").format("bigquery").save(destination_uri)
        return current_job_identifier()
```

That code belongs in a Spark integration module or optional extra, not in `FeaturePlan` or `ETLService`. The course gateway avoids importing Spark so unit tests remain fast.

## Part 5: compile the same portable subset for Beam

Implement `BeamExecutor`:

1. Store the injected `BeamGateway`.
2. Translate each feature into a mapping containing `output`, `operation`, and `inputs`.
3. Submit the transform descriptions with the dataset URIs.
4. Return a `MaterializationResult` with provider `beam`.

A production gateway would translate those descriptions into `PTransform` composition and run a `Pipeline` using DirectRunner, DataflowRunner, or another configured runner.

Do not try to hide meaningful differences:

- Spark usually centers on DataFrames, SQL expressions, partitions, and actions.
- Beam centers on `PCollection`, transforms, windowing, triggers, and runners.
- Streaming event-time semantics cannot be reduced honestly to a SQL-column mapping.

Keep only genuinely shared concepts in the core. Put framework-native transforms in framework-specific packages when portability stops helping.

## Part 6: expose ETL through the facade

Open `client.py`:

1. Import `ETLService`.
2. Add `_etl: ETLService | None = None` in the client constructor.
3. Implement a cached `etl` property just like `mlflow` and `pipelines`.

The facade groups discoverable capabilities. It does not compile expressions or hold a Spark session itself.

## Run the exercise

From `guided_mlops_sdk/learner`:

```bash
pytest -q tests/test_08_etl_and_features.py
```

Then run the cumulative suite:

```bash
pytest -q
```

Compare against these solution files only after attempting the exercise:

- `solution/src/company_mlops/etl/models.py`
- `solution/src/company_mlops/etl/plan.py`
- `solution/src/company_mlops/etl/executors.py`
- `solution/src/company_mlops/etl/service.py`
- `solution/src/company_mlops/client.py`

## What this simplified exercise deliberately omits

A real feature platform needs decisions that should not be hidden behind a generic executor:

- schema enforcement and type conversion;
- null and division-by-zero policy;
- event time, windows, and late data;
- point-in-time correctness and training-serving skew;
- partitioning and incremental backfills;
- destination write modes and idempotency;
- lineage, metrics, data-quality checks, and feature ownership;
- credentials, cluster/runner configuration, retries, and cancellation;
- serialization constraints for Python callables.

Add those only when requirements become concrete. For example, do not accept arbitrary Python callables as supposedly portable transforms: a closure that works locally may not serialize or translate correctly for Spark workers or Beam runners.

## How to test this architecture

Use different levels of tests for different risks:

1. Unit-test feature invariants and builder snapshotting without any framework.
2. Unit-test Spark and Beam compilation using recording gateways, as this exercise does.
3. Contract-test a real gateway against a tiny local Spark session or Beam DirectRunner.
4. Integration-test a small dataset in a disposable environment.
5. Compare expected rows, schemas, null behavior, and feature values—not merely whether a job reached `DONE`.

Do not make most unit tests contact Dataflow, Dataproc, BigQuery, or a remote Spark cluster.

## Choosing Spark, Beam, or neither

Choose based on your execution requirements, existing platform, and team expertise—not on SDK architecture:

- Spark is a natural fit for DataFrame/SQL-heavy batch transformations and organizations already operating Spark.
- Beam is valuable when portable runners or sophisticated streaming/event-time behavior matter.
- BigQuery SQL may be simpler for warehouse-native feature transformations.
- Pandas or Polars may be enough for small local data.

The facade/service/adapter design remains useful whichever engine you choose.

## Review questions

- Which parts of `FeaturePlan` are truly portable between Spark and Beam?
- Where should a real `SparkSession` be constructed and closed?
- Why does `ETLService` receive an executor instead of an engine-name string?
- When should a feature definition be a Pydantic model rather than a dataclass?
- How would you make a materialization write safe to retry?
- Which correctness tests would catch target leakage or incorrect point-in-time joins?

