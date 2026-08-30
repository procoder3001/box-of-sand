# Lesson 1: configuration and data models

## Why this comes first

Every later service needs configuration and exchanges data. Before constructing clients, decide which data your package trusts and which data crosses an external boundary. That determines whether a dataclass or Pydantic model is appropriate.

By the end, you will have an immutable `MLOpsConfig`, a Pydantic model for untrusted MLflow-shaped data, and a package-owned `Run` value.

## The decision

`MLOpsConfig` is a frozen dataclass because after construction it is trusted internal state. We want a small constructor, equality, a useful representation, and protection from accidental mutation. Validation in `__post_init__` protects its invariant.

`MLflowRunPayload` is a Pydantic model because dictionaries returned by an external system can be missing fields, contain wrong types, or drift. Pydantic produces structured boundary-validation errors.

`Run` is another frozen dataclass. Once the adapter validates external data, SDK users should not carry a validation framework through every domain operation.

Neither model is an ABC. ABCs describe families of implementations; these objects represent data.

## Files to edit

1. Open `learner/src/company_mlops/config.py`.
2. Implement `MLOpsConfig.__post_init__`.
3. Implement `MLOpsConfig.from_env`.
4. Read `models.py`; its two deliberately different model types are already declared.
5. Run `pytest -q tests/test_01_config_and_models.py`.

## Implementation steps

In `__post_init__`, inspect each required string. Raise the package-owned `ConfigurationError` for an empty value. A frozen dataclass can validate normally; you only need `object.__setattr__` if normalization requires changing a field.

In `from_env`, choose `os.environ` only when the injected mapping is `None`. Read the three documented names. Translate `KeyError` into `ConfigurationError` with `raise ... from error`.

Return `cls(...)`, not `MLOpsConfig(...)`. `cls` lets an inherited alternate constructor produce a subclass.

## Why `@classmethod` here?

The normal constructor accepts already parsed values:

```python
MLOpsConfig("project", "us-central1", "https://tracking")
```

`from_env` is a named alternate input route. It performs environment-specific reading and then delegates invariant enforcement to the normal constructor. A standalone function could work, but the classmethod makes discovery natural and preserves subclass construction.

Do not read environment variables in class attributes or module-level code. That freezes state at import time and makes tests order-dependent.

## Hints

- The solution imports both `os` and `ConfigurationError`.
- `error.args[0]` contains the missing mapping key.
- Pydantic's `extra="forbid"` catches unnoticed upstream response drift.

## Apply this to your SDK

Keep one configuration snapshot underneath your facade. If YAML or CLI input is complex and untrusted, validate a Pydantic settings/input model at that outer boundary and convert it to your internal configuration. Avoid passing raw dictionaries through GCP and MLflow services.

## Check your understanding

- Why is a mutable dataclass dangerous for a config shared by several resources?
- Why not expose `MLflowRunPayload` as the public run type?
- When would a plain function `config_from_env()` be simpler and completely adequate?

Compare with `solution/src/company_mlops/config.py` and `models.py` only after attempting the test.

