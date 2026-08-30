# SDK engineering practice

These eleven exercises turn the Python and SDK-design flashcards into small implementation drills. Each exercise has:

- `starter/<exercise>/sdk.py`: the file to complete.
- `starter/<exercise>/test_sdk.py`: executable requirements; do not edit it on the first pass.
- `solutions/<exercise>/sdk.py`: one complete design, not the only valid design.
- `solutions/<exercise>/test_sdk.py`: the same tests, so the reference implementation can be checked independently.

Exercises 01–08 and 11 use only the Python standard library and run on Python 3.10+. Exercise 09 intentionally requires Python 3.12+ so you practice PEP 695 syntax directly. Exercise 10 requires Pydantic v2; install its local `requirements.txt` in your own virtual environment.

## Practice loop

Run one starter test from the repository root:

```bash
python3 -m unittest discover exercises/starter/01_value_objects -v
```

Work only in that exercise's `sdk.py` until the tests pass. Then compare your code with the matching solution. Do not merely check whether the lines match: explain why each class owns its particular responsibility.

Check every reference solution at once:

```bash
for directory in exercises/solutions/*; do
  python3 -m unittest discover "$directory" -v || exit 1
done
```

For retention, repeat an exercise from a clean starter after 1 day, 1 week, and 1 month. On the later attempts, add one change from the “stretch” prompt before looking at the solution.

## Progression

| Exercise | Main ideas | Design question |
|---|---|---|
| 01 | dataclasses, frozen values, `default_factory`, properties, class methods | Which state is a value, and where should validation happen? |
| 02 | ABCs, `Protocol`, `TypeVar`, generics, dependency injection | Do callers need nominal inheritance or only a capability? |
| 03 | decorators, closures, `Callable`, `ParamSpec`, `wraps` | Can cross-cutting behavior preserve the wrapped API? |
| 04 | explicit clients, resource objects, injected transport, lazy properties | How do you expose a pleasant public API without global state? |
| 05 | adapters, factories, registries, `__init_subclass__` | When is a registry useful, and when is a dictionary enough? |
| 06 | iterators, generators, generic pages, lazy pagination | Can callers consume large collections without eager loading? |
| 07 | context managers, exception translation/chaining, cleanup | Who owns a resource, and which errors belong in the public API? |
| 08 | thin CLI, service layer, fakes, exit codes | Can library and CLI users share exactly the same behavior? |
| 09 | Python 3.12 type parameters and aliases, bounded generics | Does the type parameter preserve a useful relationship for callers? |
| 10 | Pydantic, dataclasses, ABCs, protocols, ordinary classes | Is this type validating data, representing a value, specifying a contract, or coordinating behavior? |
| 11 | async context managers, timeouts, cancellation, bounded concurrency | Does async work remain cancellable, bounded, and correctly cleaned up? |

## Rules of thumb while solving

1. Start from the public behavior expressed by the tests.
2. Prefer the smallest abstraction that meets that behavior.
3. Keep network-shaped dependencies injectable.
4. Keep transport dictionaries and transport exceptions behind the SDK boundary.
5. Avoid work at import time.
6. Make ownership and cleanup explicit.

The retry exercise is intentionally educational. In production, normally configure an established retry facility and confirm idempotency before retrying writes.

## Stretch prompts for later repetitions

- **01:** Add a `from_uri()` alternate constructor to `ArtifactRef` and reject non-`gs` schemes.
- **02:** Add a second `BlobStore` fake that records calls, then reuse the same contract tests for both stores.
- **03:** Inject a `before_retry(exception, attempt)` callback without losing the decorated signature.
- **04:** Add a `DeploymentsResource`; verify that both resources share one transport but remain independently cached.
- **05:** First replace `__init_subclass__` with an explicit dictionary registration function. Decide which version is clearer for three known adapters.
- **06:** Add a `limit` that stops iteration without fetching an unnecessary page.
- **07:** Translate status 404 into a new `ArtifactNotFoundError`, while allowing unknown transport failures through unchanged.
- **08:** Add a second adapter (a small HTTP-handler-shaped function) that invokes the same `DeploymentService`; no validation may be duplicated.
- **09:** Add a generic `first[T](items: Iterable[T]) -> T` function, then explain why a function returning only `int` would not benefit from `T`.
- **10:** Add a Pydantic request model with an alias for one wire-format field. Keep that alias out of the internal dataclass.
- **11:** Change the client to return results as they complete with an async iterator, while preserving bounded concurrency and cancellation cleanup.

## Choosing a Python type in an SDK

Use the role of the type—not its popularity—to choose the construct:

- Use a Pydantic model to parse and validate untrusted dictionaries, JSON responses, configuration, or user input at a boundary.
- Use a dataclass for trusted internal values and state where automatic construction, equality, and representation are useful.
- Use a frozen dataclass for immutable identifiers, references, and configuration snapshots.
- Use an ABC when implementations intentionally join an SDK-owned inheritance family, especially when the base supplies shared behavior.
- Use a protocol when injected collaborators only need to provide a capability and should not be forced to inherit from your package.
- Use an ordinary class for stateful clients, resource groups, and service orchestration.

These constructs solve different problems and often appear together. Pydantic and dataclasses model data; ABCs and protocols describe implementation contracts.
