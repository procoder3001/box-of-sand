# Lesson 7: thin CLI and package wiring

## The required direction of calls

```text
console entry point
  → parse syntax
  → MLOpsClient public API
  → service/domain validation
  → adapter/backend
```

The CLI is another adapter. It must not contain an alternative implementation of experiment creation.

## Files to edit

1. Implement `run_cli` in `cli.py`.
2. Inspect `main`; it deliberately marks where real production dependencies would be wired.
3. Inspect the console entry under `[project.scripts]` in `pyproject.toml`.
4. Inspect `__init__.py` and its deliberately small `__all__`.
5. Run `pytest -q tests/test_07_cli_and_public_api.py` and then `pytest -q`.

## Parsing and translation

Use `argparse.ArgumentParser(exit_on_error=False)` and subparsers for:

```text
company-mlops experiment create NAME
```

After parsing, call only:

```python
client.mlflow.experiments.create(arguments.name)
```

Print the resulting ID to the injected `stdout`. Translate expected parsing, SDK, and domain-validation errors into a message on `stderr` and exit code 2. Let unexpected errors propagate.

Injecting streams and the client makes CLI tests deterministic and prevents contact with real services.

## Composition root

`main()` is the narrow place where a production program may:

- read environment-backed configuration;
- construct the real MLflow/GCP clients;
- wrap them in adapters;
- construct `MLOpsClient`;
- call `run_cli`.

Do none of this at module import time. Library users importing `Run` must not trigger credential discovery or network setup.

In a real Click CLI, the same layering applies. Click decorators belong on thin command functions; the command invokes the public service. Use `CliRunner` for the Click adapter and ordinary unit tests for services.

## Public imports

`company_mlops.__init__` re-exports only stable, intentional names. Internal adapters remain importable by maintainers but are not promised as the primary public API. A smaller surface makes compatibility and deprecation manageable.

## Apply this to your SDK

Create package directories by capability, not by design-pattern name. Prefer `mlflow/runs.py` over `factories/run_factory.py`. Keep `pyproject.toml`, `config.py`, `client.py`, `errors.py`, and the public imports understandable before adding many integrations.

## Final architecture review

For each external operation, you should now be able to locate:

- its public entry on the facade/resource;
- domain validation in the service;
- third-party translation in the adapter;
- dependency contract in a protocol;
- data shape at the boundary and the internal value;
- a fake-driven unit test;
- lifecycle ownership and error behavior.

## Check your understanding

- Why should the CLI call the same API as notebooks and tests?
- Which exceptions should become friendly exit code 2 errors?
- What belongs in `main()` but not in `MLOpsClient.__init__`?
- Which three names should your first public `__init__.py` expose—and why only those?

