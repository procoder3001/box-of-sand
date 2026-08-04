# Python Basics: Prerequisite Flashcards

This deck is meant to be studied before `flashcards.md`. It teaches the Python vocabulary and everyday mechanics assumed by the advanced package-engineering deck. The examples use small MLOps-flavored scenarios, but the lessons are general Python.

### Front

What values do these variables hold, and why are the type annotations useful?

```python
run_name: str = "daily-training"
max_attempts: int = 3
learning_rate: float = 0.01
dry_run: bool = True
```

### Back

They hold a string, integer, floating-point number, and Boolean. A variable is a name bound to an object. The annotations document the intended types and help static type checkers, but Python does not enforce them automatically at runtime.

```python
max_attempts = "three"  # Runs, but a type checker should flag it.
```

**Application:** Annotate public functions and important configuration so callers and tools can understand the contract.

**Card ID:** B001
**Tags:** variables, primitive-types, type-annotations
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — an informal introduction](https://docs.python.org/3/tutorial/introduction.html)

---CARD---

### Front

Does assigning `backup = config` copy the dictionary?

```python
config = {"retries": 3}
backup = config
config["retries"] = 5

print(backup["retries"])
```

### Back

No. Assignment binds another name to the same object, so it prints `5`. Python variables contain references to objects rather than independent boxes that automatically copy values.

```python
assert backup is config
assert id(backup) == id(config)
```

`id` is useful for learning and debugging identity, but application logic should normally use values and explicit ownership rules.

**Application:** Be clear about whether configuration passed between layers is intentionally shared or should be copied.

**Card ID:** B037
**Tags:** memory, references, assignment, identity
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python language reference — objects, values, and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)

---CARD---

### Front

Why does `models` change but `run_name` not change through the alias?

```python
models = ["v1"]
same_models = models
models.append("v2")

run_name = "nightly"
same_name = run_name
run_name = "weekly"
```

### Back

`append` mutates the existing list observed through both names. Assigning `"weekly"` rebinds `run_name` to another string; it does not alter the original immutable string referenced by `same_name`.

```python
assert same_models == ["v1", "v2"]
assert same_name == "nightly"
assert models is same_models
```

**Application:** Most aliasing bugs arise from confusing mutation of an object with rebinding of a name.

**Card ID:** B038
**Tags:** memory, mutation, rebinding, immutability
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python language reference — objects, values, and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)

---CARD---

### Front

Why does a shallow copy fail to isolate the nested list?

```python
original = {"labels": ["nightly"]}
copied = original.copy()
copied["labels"].append("gpu")

print(original)
```

### Back

A shallow copy creates a new outer dictionary but inserts references to the same child objects. Both dictionaries therefore refer to one labels list.

```python
assert copied is not original
assert copied["labels"] is original["labels"]
assert original == {"labels": ["nightly", "gpu"]}
```

**Application:** A shallow copy is sufficient when nested values are immutable or intentionally shared.

**Card ID:** B039
**Tags:** memory, shallow-copy, nested-objects
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — shallow and deep copy operations](https://docs.python.org/3/library/copy.html)

---CARD---

### Front

When does `deepcopy` solve a real problem?

```python
from copy import deepcopy

template = {"training": {"tags": ["nightly"]}}
run_config = deepcopy(template)
run_config["training"]["tags"].append("gpu")
```

### Back

Use `deepcopy` when you need an independent clone of a nested mutable object graph and later mutations must not reach the original.

```python
assert template["training"]["tags"] == ["nightly"]
assert run_config["training"]["tags"] == ["nightly", "gpu"]
```

`deepcopy` keeps a memo so cycles terminate and shared relationships can be preserved within the copied graph.

**Application:** It can isolate a per-run configuration derived from a nested mutable template.

**Card ID:** B040
**Tags:** memory, deepcopy, configuration
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — `copy.deepcopy`](https://docs.python.org/3/library/copy.html#copy.deepcopy)

---CARD---

### Front

Why should you not automatically use `deepcopy` everywhere?

```python
from copy import deepcopy

class Service:
    def __init__(self, client: object) -> None:
        self.client = client

service_copy = deepcopy(Service(client=object()))
```

### Back

Deep copying can be expensive, copy too much, duplicate objects that represent external resources, or produce surprising results for custom classes. Files, locks, sessions, and clients usually have ownership rules rather than meaningful cloned state.

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class RunConfig:
    retries: int

updated = replace(RunConfig(3), retries=5)
```

**Application:** Prefer immutable configuration, constructors, or targeted copies when the intended boundary is known.

**Card ID:** B041
**Tags:** memory, deepcopy, resource-ownership, immutable-data
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — copying caveats](https://docs.python.org/3/library/copy.html)

---CARD---

### Front

Are function arguments copied when a function is called?

```python
def add_tag(tags: list[str]) -> None:
    tags.append("validated")

run_tags = ["nightly"]
add_tag(run_tags)
```

### Back

No automatic object copy occurs. The local parameter is bound to the object supplied by the caller, so mutation is visible afterward.

```python
assert run_tags == ["nightly", "validated"]

def with_tag(tags: list[str]) -> list[str]:
    return [*tags, "validated"]
```

The second design returns a fresh list and makes the lack of caller mutation easier to reason about.

**Application:** Document mutating APIs clearly; package boundaries often benefit from returning new values.

**Card ID:** B042
**Tags:** memory, functions, mutation, api-design
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)

---CARD---

### Front

How can an immutable tuple appear to change?

```python
record = (["model.pkl"], "complete")
record[0].append("metrics.json")
```

### Back

The tuple itself is unchanged: it still refers to the same two objects. Its first object is a mutable list, and that list changed. Container immutability is not deep immutability.

```python
assert record == (["model.pkl", "metrics.json"], "complete")

safer = (("model.pkl",), "complete")
```

**Application:** Use immutable nested values when a configuration or cache key must remain stable.

**Card ID:** B043
**Tags:** memory, tuple, shallow-immutability
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — immutable sequence types](https://docs.python.org/3/library/stdtypes.html#immutable-sequence-types)

---CARD---

### Front

Why do `+=` and `+` behave differently for this list alias?

```python
first = ["extract"]
alias = first
first += ["train"]

second = ["extract"]
other_alias = second
second = second + ["train"]
```

### Back

For lists, `+=` normally extends the existing object in place, so `alias` sees the change. `+` creates a new list and the assignment rebinds only `second`.

```python
assert alias == ["extract", "train"]
assert first is alias
assert other_alias == ["extract"]
assert second is not other_alias
```

**Application:** Avoid relying on augmented-assignment details in shared-state code; make mutation or new-value creation obvious.

**Card ID:** B044
**Tags:** memory, augmented-assignment, mutation
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python language reference — augmented assignment](https://docs.python.org/3/reference/simple_stmts.html#augmented-assignment-statements)

---CARD---

### Front

Does `del client` immediately destroy the client object?

```python
client = object()
alias = client
del client

print(alias)
```

### Back

`del client` removes that name binding. The object remains reachable through `alias`. Object lifetime depends on reachability, not on deleting one particular variable.

```python
value = [1, 2]
alias = value
del value
assert alias == [1, 2]
```

CPython commonly reclaims non-cyclic objects when their reference count reaches zero, but code should not depend on a particular interpreter's collection timing.

**Application:** Use context managers for prompt cleanup of files and sessions rather than relying on garbage collection.

**Card ID:** B045
**Tags:** memory, del, lifetime, reference-counting
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python language reference — the `del` statement](https://docs.python.org/3/reference/simple_stmts.html#the-del-statement)

---CARD---

### Front

Why can reference counting alone not reclaim this object?

```python
items: list[object] = []
items.append(items)
del items
```

### Back

The list refers to itself, creating a reference cycle. After the external name disappears, the cycle is unreachable but its internal reference remains. Python's cyclic garbage collector can detect such unreachable cycles.

```python
import gc

reclaimed = gc.collect()  # Mainly useful for diagnostics/tests.
print(reclaimed)
```

Manual collection is rarely an application fix; lingering memory more often comes from still-reachable caches, globals, callbacks, or queues.

**Application:** Diagnose unexpected retention by finding what still owns an object before reaching for `gc.collect()`.

**Card ID:** B046
**Tags:** memory, garbage-collection, cycles, ownership
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [Python library reference — `gc`](https://docs.python.org/3/library/gc.html)

---CARD---

### Front

What is the difference between `pyproject.toml`, `uv.lock`, and `.venv`?

```python
team_files = {
    "pyproject.toml": "declared project requirements",
    "uv.lock": "exact resolved dependency graph",
    ".venv": "one developer's installed environment",
}
```

### Back

`pyproject.toml` states direct dependencies and acceptable constraints. `uv.lock` records the reproducible resolution, including transitive packages. `.venv` is generated local state.

```python
commit_to_git = ["pyproject.toml", "uv.lock"]
ignore_in_git = [".venv/"]
```

**Application:** Teammates review declared intent and the resulting lockfile, then independently recreate the environment.

**Card ID:** B047
**Tags:** uv, pyproject, lockfile, virtual-environment
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [uv documentation — project structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)

---CARD---

### Front

How should a developer add a runtime dependency with `uv`?

```python
commands = [
    "git switch -c add-http-client",
    "uv add httpx",
    "uv run pytest",
]
```

### Back

`uv add httpx` updates the project dependency declaration, resolves the graph, updates `uv.lock`, and updates the project environment. Review and commit both metadata files together.

```python
files_to_review = ["pyproject.toml", "uv.lock"]
```

Do not use `uv pip install` to make an undeclared, persistent project dependency; teammates and CI would not learn that requirement.

**Application:** One focused dependency change per branch makes resolution changes easier to review.

**Card ID:** B048
**Tags:** uv, dependencies, collaboration
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [uv documentation — managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)

---CARD---

### Front

Where should `pytest` and `ruff` be declared if users of your library do not need them?

```python
commands = [
    "uv add --dev pytest",
    "uv add --group lint ruff",
]
```

### Back

Put development-only tools in dependency groups, not runtime `project.dependencies`. `--dev` targets the conventional `dev` group; named groups can separate linting, docs, or other workflows.

```python
dependency_groups = {
    "dev": ["pytest"],
    "lint": ["ruff"],
}
```

Published optional features belong in `project.optional-dependencies`; local developer tooling belongs in dependency groups.

**Application:** This keeps the install surface for library users smaller while giving contributors reproducible tools.

**Card ID:** B049
**Tags:** uv, dependency-groups, dev-dependencies, extras
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [uv documentation — development dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies)

---CARD---

### Front

What should a teammate do after pulling changes to `pyproject.toml` and `uv.lock`?

```python
after_git_pull = [
    "uv sync",
    "uv run pytest",
]
```

### Back

`uv sync` installs the locked project environment. Its default exact sync removes packages not represented in the lockfile, preventing accidental local extras from hiding missing declarations.

```python
ci_commands = [
    "uv sync --locked",
    "uv run --locked pytest",
]
```

`--locked` makes stale lock metadata an error rather than silently changing it, which is useful in CI.

**Application:** Teammates reproduce the committed resolution instead of independently resolving whatever happens to be newest.

**Card ID:** B050
**Tags:** uv, sync, lockfile, ci
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [uv documentation — locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)

---CARD---

### Front

Why should upgrading one package be an intentional change?

```python
commands = [
    "uv lock --upgrade-package httpx",
    "uv run pytest",
]
```

### Back

With a lockfile, uv prefers already locked versions. `--upgrade-package` asks it to update the named package within declared constraints while retaining other locked versions where possible.

```python
broad_upgrade = "uv lock --upgrade"
focused_upgrade = "uv lock --upgrade-package httpx"
```

A focused upgrade produces a smaller diff and clearer test scope. Broad upgrades are legitimate maintenance tasks but should not be accidental side effects of unrelated feature work.

**Application:** Review lockfile diffs and test integration boundaries affected by the upgraded package.

**Card ID:** B051
**Tags:** uv, upgrades, lockfile, code-review
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [uv documentation — upgrading locked package versions](https://docs.astral.sh/uv/concepts/projects/sync/#upgrading-locked-package-versions)

---CARD---

### Front

Two developers changed dependencies and Git reports a conflict in `uv.lock`. What should they do?

```python
safe_sequence = [
    "resolve pyproject.toml intentionally",
    "regenerate uv.lock with uv lock",
    "run uv sync and tests",
]
```

### Back

First merge the human-authored dependency intent in `pyproject.toml`. Then let uv compute a coherent lockfile from that result. Do not hand-splice arbitrary lockfile sections or simply choose one branch if both added requirements.

```python
verification = [
    "uv lock --check",
    "uv run --locked pytest",
]
```

Inspect the regenerated diff for unexpected removals, source changes, or broad upgrades before committing it.

**Application:** The resolver should decide the transitive graph; developers decide the direct requirements and constraints.

**Card ID:** B052
**Tags:** uv, merge-conflicts, lockfile, teamwork
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [uv documentation — locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)

---CARD---

### Front

How does `requires-python` participate in dependency resolution?

```python
pyproject_fragment = '''
[project]
requires-python = ">=3.11,<3.14"
'''
```

### Back

The supported Python range is part of the package contract. uv must select dependency versions compatible with that range, not merely the interpreter used by one developer.

```python
supported_ci = ["3.11", "3.12", "3.13"]
```

Set the range deliberately and test supported versions. Narrowing it can exclude users; leaving it inaccurate can produce installations that resolve but fail at runtime.

**Application:** Agree on supported Python versions before resolving disagreements caused by version-specific dependencies.

**Card ID:** B053
**Tags:** uv, python-versions, constraints, compatibility
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [uv documentation — Python version requirement](https://docs.astral.sh/uv/concepts/projects/config/#python-version-requirement)

---CARD---

### Front

What does “no solution found” usually mean?

```python
requirements = [
    "analytics-core<2",
    "new-plugin>=4",  # Suppose this requires analytics-core>=2.
]
```

### Back

The combined constraints cannot all be true in the resolved environment. Read the resolver's explanation to locate the incompatible chain; do not randomly pin transitive packages until the message disappears.

```python
questions = [
    "Can either direct constraint be widened?",
    "Is a compatible plugin version available?",
    "Are these features truly installed together?",
]
```

If two dependency groups are intentionally mutually exclusive, uv can model declared conflicts, but that adds operational complexity.

**Application:** Resolve conflicts by clarifying the supported product combination, not merely by coercing the solver.

**Card ID:** B054
**Tags:** uv, resolution, constraints, dependency-conflicts
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [uv documentation — conflicting dependencies](https://docs.astral.sh/uv/concepts/projects/config/#conflicting-dependencies)

---CARD---

### Front

Why should a package library avoid exact pins for every runtime dependency in `pyproject.toml`?

```python
library_constraints = [
    "click>=8.1,<9",
    "httpx>=0.27,<1",
]
```

### Back

Library requirements must coexist with the consuming application's requirements. Unnecessarily exact pins reduce the versions that can satisfy both. Use the narrowest constraints justified by real compatibility; let `uv.lock` capture exact versions for development and CI.

```python
declared_intent = "httpx>=0.27,<1"
locked_example = "httpx==0.28.1"  # Conceptual resolved version.
```

An application may choose tighter pins because it owns the final environment.

**Application:** Test the supported range and add upper bounds when incompatibility is known, not from reflex.

**Card ID:** B055
**Tags:** uv, libraries, version-constraints, lockfile
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [uv documentation — dependency specifiers](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-specifiers)

---CARD---

### Front

How should a team configure a private package index without committing credentials?

```python
safe_repository_data = {
    "index_name": "internal",
    "index_url": "https://packages.example.invalid/simple",
    "password": None,
}
```

### Back

Commit non-secret index identity and policy only when appropriate. Supply credentials through supported environment variables or credential mechanisms in developer and CI environments. Never place tokens in `pyproject.toml`, `uv.lock`, or a Git URL.

```python
def redact(url: str) -> str:
    return url.split("@")[-1]
```

Also decide which packages may come from which indexes to reduce dependency-confusion risk; do not treat every configured index as interchangeable.

**Application:** Document authentication setup separately so every contributor follows the same secure workflow.

**Card ID:** B056
**Tags:** uv, private-index, credentials, supply-chain
**Difficulty:** Intermediate
**Source type:** Official documentation
**Source:** [uv documentation — package indexes](https://docs.astral.sh/uv/concepts/indexes/)

---CARD---

### Front

What is the difference between `==` and `is`?

```python
expected = ["model.pkl"]
actual = ["model.pkl"]

print(actual == expected)
print(actual is expected)
```

### Back

`==` compares values, so the first result is `True`. `is` compares object identity, so the second is `False`: these are two different lists. Use `is` for singletons such as `None`.

```python
artifact_uri: str | None = None
if artifact_uri is None:
    print("No artifact was produced")
```

**Application:** Value comparison is common in validation and tests; identity comparison is rarely the intended choice except for `None` or explicit sentinels.

**Card ID:** B002
**Tags:** equality, identity, none
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python language reference — comparisons](https://docs.python.org/3/reference/expressions.html#comparisons)

---CARD---

### Front

Which values are “falsy,” and what will this code print?

```python
artifacts: list[str] = []

if artifacts:
    print("uploading")
else:
    print("nothing to upload")
```

### Back

It prints `nothing to upload`. Empty collections, zero, empty strings, `None`, and `False` are falsy. Most other objects are truthy.

```python
if not artifacts:
    print("nothing to upload")
```

Be careful when `0`, `""`, and `None` have different meanings; test explicitly in that case.

**Application:** Truth testing keeps simple collection checks readable, but configuration validation sometimes needs `value is None` rather than `not value`.

**Card ID:** B003
**Tags:** booleans, truthiness, conditionals
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — truth value testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)

---CARD---

### Front

When should you use a list, tuple, set, or dictionary?

```python
steps = ["extract", "train"]
location = (51.5, -0.1)
tags = {"nightly", "gpu"}
metrics = {"accuracy": 0.94}
```

### Back

A list is an ordered mutable sequence; a tuple is an ordered fixed-size record or immutable sequence; a set stores unique values; a dictionary maps unique keys to values.

```python
steps.append("deploy")
tags.add("validated")
metrics["loss"] = 0.12
```

**Application:** Choose the collection whose behavior expresses the domain: ordered pipeline steps, unique labels, or metric-name lookup.

**Card ID:** B004
**Tags:** list, tuple, set, dictionary
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — data structures](https://docs.python.org/3/tutorial/datastructures.html)

---CARD---

### Front

Why does indexing start at zero, and what do these slices return?

```python
runs = ["r1", "r2", "r3", "r4"]
print(runs[0])
print(runs[-1])
print(runs[1:3])
```

### Back

Python sequences use zero-based indexes. Index `0` is the first element, `-1` is the last, and a slice includes its start but excludes its stop. The outputs are `r1`, `r4`, and `["r2", "r3"]`.

```python
first_two = runs[:2]
remaining = runs[2:]
copy = runs[:]
```

**Application:** Slices are useful for small batches, but slicing a list creates another list and can consume memory.

**Card ID:** B005
**Tags:** sequences, indexing, slicing
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — strings and slicing](https://docs.python.org/3/tutorial/introduction.html#strings)

---CARD---

### Front

What is the difference between mutating a list and creating a new one?

```python
original = ["train"]
alias = original
alias.append("deploy")

print(original)
```

### Back

It prints `["train", "deploy"]`. Both names refer to the same mutable list, and `append` changes that object. Copy when independent mutation is intended.

```python
original = ["train"]
independent = original.copy()
independent.append("deploy")
```

A shallow copy does not recursively copy nested mutable objects.

**Application:** Shared mutable configuration can cause distant, surprising changes. Prefer creating fresh values at boundaries.

**Card ID:** B006
**Tags:** mutability, references, copying
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — more on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)

---CARD---

### Front

How do `if`, `elif`, and `else` select one path?

```python
status_code = 503

if status_code == 404:
    result = "missing"
elif status_code >= 500:
    result = "service failure"
else:
    result = "other"
```

### Back

Conditions are checked from top to bottom, and only the first matching branch runs. Here `result` becomes `"service failure"`.

```python
if 200 <= status_code < 300:
    result = "success"
```

Python permits chained comparisons, which are often clearer than two comparisons joined by `and`.

**Application:** Keep branching rules explicit in domain functions so both a CLI and library API can reuse them.

**Card ID:** B007
**Tags:** conditionals, comparisons, control-flow
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — `if` statements](https://docs.python.org/3/tutorial/controlflow.html#if-statements)

---CARD---

### Front

What does this loop do, and how can `enumerate` improve it?

```python
steps = ["extract", "train", "evaluate"]
for step in steps:
    print(step)
```

### Back

The loop visits each item in order. Use `enumerate` when you need the position as well as the value.

```python
for position, step in enumerate(steps, start=1):
    print(position, step)
```

Do not manually maintain an index unless its update rules genuinely differ from the iteration.

**Application:** Iteration is clearer and safer than indexing when processing batches of artifacts or pipeline steps.

**Card ID:** B008
**Tags:** for-loop, iteration, enumerate
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — looping techniques](https://docs.python.org/3/tutorial/datastructures.html#looping-techniques)

---CARD---

### Front

When is a `while` loop appropriate, and why must its state change?

```python
attempt = 0
while attempt < 3:
    print(f"attempt {attempt + 1}")
    attempt += 1
```

### Back

A `while` loop repeats while a condition remains true. Its controlling state normally needs to change, or the loop can run forever.

```python
while True:
    message = receive_message()
    if message is None:
        break
    process(message)
```

**Application:** Use `while` for condition-driven work. For retrying network calls, prefer a proven retry library rather than hand-writing a loop.

**Card ID:** B009
**Tags:** while-loop, break, control-flow
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — `break` and `continue`](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements)

---CARD---

### Front

What does a function parameter receive, and what does `return` do?

```python
def make_uri(bucket: str, name: str) -> str:
    return f"gs://{bucket}/{name}"

uri = make_uri("models", "latest.pkl")
```

### Back

Parameters are local names bound to the arguments supplied by the caller. `return` stops the function and gives a value back. Here `uri` is `"gs://models/latest.pkl"`.

```python
def log_upload(name: str) -> None:
    print(f"uploaded {name}")
```

`-> None` says the function is called for its effect rather than a useful return value.

**Application:** Small functions with clear inputs and outputs are easy to reuse from library code, Click commands, and tests.

**Card ID:** B010
**Tags:** functions, parameters, return-values
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)

---CARD---

### Front

Why is this default argument dangerous?

```python
def add_tag(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags
```

### Back

Default arguments are evaluated once when the function is defined. Every call that omits `tags` reuses the same list.

```python
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    result = [] if tags is None else tags.copy()
    result.append(tag)
    return result
```

**Application:** Use `None` plus creation inside the function for mutable defaults. The advanced deck applies the same idea to dataclass `default_factory`.

**Card ID:** B011
**Tags:** functions, defaults, mutability
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — default argument values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)

---CARD---

### Front

What are positional and keyword arguments?

```python
def start_run(name: str, *, dry_run: bool = False) -> None:
    print(name, dry_run)

start_run("nightly", dry_run=True)
```

### Back

`"nightly"` is passed by position. `dry_run=True` is passed by name. The `*` makes later parameters keyword-only, so their meaning is visible at the call site.

```python
start_run("nightly", True)  # TypeError: dry_run is keyword-only
```

**Application:** Keyword-only options prevent ambiguous calls when a public API has several flags, timeouts, or identifiers.

**Card ID:** B012
**Tags:** functions, arguments, keyword-only
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — special parameters](https://docs.python.org/3/tutorial/controlflow.html#special-parameters)

---CARD---

### Front

What scope does each `run_id` belong to?

```python
run_id = "global"

def show_run() -> None:
    run_id = "local"
    print(run_id)

show_run()
print(run_id)
```

### Back

Assignment inside the function creates a local name, so the output is `local` and then `global`. A function can read a global name, but local state and explicit parameters are usually easier to understand and test.

```python
def show_run(run_id: str) -> None:
    print(run_id)

show_run("explicit")
```

**Application:** Passing clients and configuration explicitly avoids hidden global dependencies.

**Card ID:** B013
**Tags:** scope, local-variables, globals
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — scopes and namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)

---CARD---

### Front

What is a list comprehension doing here?

```python
scores = [0.72, 0.91, 0.88]
passing = [score for score in scores if score >= 0.85]
```

### Back

It builds a new list by transforming or filtering an iterable. `passing` becomes `[0.91, 0.88]`.

```python
passing = []
for score in scores:
    if score >= 0.85:
        passing.append(score)
```

The loop is equivalent and may be clearer when logic becomes complex.

**Application:** Comprehensions are good for small, readable data transformations—not multi-step business workflows or hidden side effects.

**Card ID:** B014
**Tags:** comprehensions, lists, filtering
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — list comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)

---CARD---

### Front

What problem do `try` and `except` solve?

```python
raw_timeout = "fast"
try:
    timeout = int(raw_timeout)
except ValueError:
    timeout = 30
```

### Back

They let code handle an expected failure without terminating the whole program. Catch the narrow exception you understand; broad `except Exception` blocks can hide programming bugs.

```python
def parse_timeout(value: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"invalid timeout: {value!r}") from error
```

**Application:** Translate low-level failures into meaningful package errors at a boundary, while preserving the original cause.

**Card ID:** B015
**Tags:** exceptions, try-except, error-handling
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — handling exceptions](https://docs.python.org/3/tutorial/errors.html#handling-exceptions)

---CARD---

### Front

When should a function `raise` an exception?

```python
def validate_replicas(replicas: int) -> None:
    if replicas < 1:
        raise ValueError("replicas must be positive")
```

### Back

Raise when the function cannot honor its contract. The caller can catch the exception, log it, translate it for a CLI, or let it propagate.

```python
try:
    validate_replicas(0)
except ValueError as error:
    print(f"Configuration error: {error}")
```

**Application:** Library functions should raise meaningful exceptions instead of printing an error and exiting the process.

**Card ID:** B016
**Tags:** exceptions, raise, validation
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions)

---CARD---

### Front

Why is `with` preferred when opening a file?

```python
from pathlib import Path

with Path("metrics.txt").open(encoding="utf-8") as file:
    metrics = file.read()
```

### Back

The context manager closes the file when the block ends, including when an exception occurs. It makes resource ownership and cleanup explicit.

```python
path = Path("metrics.txt")
path.write_text("accuracy=0.94\n", encoding="utf-8")
```

**Application:** The same `with` protocol manages files, MLflow runs, locks, temporary directories, and network resources.

**Card ID:** B017
**Tags:** files, context-managers, cleanup
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)

---CARD---

### Front

What do imports do, and why should modules avoid expensive work at import time?

```python
# cli.py
from pathlib import Path

def load_config(path: Path) -> str:
    return path.read_text(encoding="utf-8")
```

### Back

Importing executes a module's top-level statements once and makes its names available. Defining functions and classes is normal; contacting a cloud service or loading a large model during import makes startup fragile and slow.

```python
# Good: work happens only when called.
def make_client() -> object:
    return create_cloud_client()
```

**Application:** Cheap imports keep library use, tests, and CLI `--help` reliable.

**Card ID:** B018
**Tags:** modules, imports, side-effects
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — modules](https://docs.python.org/3/tutorial/modules.html)

---CARD---

### Front

What is the purpose of this class and its `self` parameter?

```python
class Run:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id

    def label(self) -> str:
        return f"run:{self.run_id}"
```

### Back

A class defines behavior shared by its instances. `__init__` initializes a new instance, and `self` refers to the particular instance receiving a method call.

```python
run = Run("r-123")
print(run.run_id)
print(run.label())
```

**Application:** Use a class when state and behavior belong together. A function is simpler when no lasting state is needed.

**Card ID:** B019
**Tags:** classes, objects, methods
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — classes](https://docs.python.org/3/tutorial/classes.html#a-first-look-at-classes)

---CARD---

### Front

What is the difference between an instance attribute and a class attribute?

```python
class Job:
    platform = "gcp"

    def __init__(self, name: str) -> None:
        self.name = name
```

### Back

`platform` belongs to the class and is shared as a default by instances. `name` is stored separately on each instance.

```python
first = Job("train")
second = Job("deploy")
print(first.platform, first.name)
print(second.platform, second.name)
```

Avoid mutable class attributes for per-instance data because all instances would share them.

**Application:** Constants can be class attributes; client sessions, tags, and configuration normally belong to instances.

**Card ID:** B020
**Tags:** classes, attributes, shared-state
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — class and instance variables](https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables)

---CARD---

### Front

What benefit does this dataclass provide?

```python
from dataclasses import dataclass

@dataclass
class ModelRef:
    name: str
    version: int
```

### Back

`@dataclass` generates common methods such as `__init__`, `__repr__`, and value-based `__eq__` from annotated fields.

```python
first = ModelRef("fraud", 3)
second = ModelRef(name="fraud", version=3)
assert first == second
```

**Application:** Dataclasses are good for configuration, identifiers, and results that mostly carry data. Use a regular class when initialization or behavior is complex.

**Card ID:** B021
**Tags:** dataclasses, classes, value-objects
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — `dataclasses`](https://docs.python.org/3/library/dataclasses.html)

---CARD---

### Front

What does inheritance do in this example?

```python
class PackageError(Exception):
    pass

class AuthenticationError(PackageError):
    pass
```

### Back

`AuthenticationError` is a more specific kind of `PackageError`. A caller may catch only authentication failures or catch the package-wide base class.

```python
try:
    raise AuthenticationError("credentials expired")
except PackageError as error:
    print(error)
```

**Application:** Exception inheritance gives callers stable recovery categories. Prefer composition over inheritance for most ordinary application objects.

**Card ID:** B022
**Tags:** inheritance, exceptions, class-hierarchies
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — user-defined exceptions](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)

---CARD---

### Front

What does `str | None` mean, and why must the code check it?

```python
def find_uri(name: str) -> str | None:
    if name == "latest":
        return "gs://models/latest.pkl"
    return None
```

### Back

The function returns either a string or `None`. The caller must narrow the possibilities before using string methods.

```python
uri = find_uri("latest")
if uri is None:
    raise LookupError("model not found")
print(uri.removeprefix("gs://"))
```

**Application:** Optional return types make absence explicit. Raise an exception instead when absence means the operation failed rather than a normal result.

**Card ID:** B023
**Tags:** typing, union-types, none, narrowing
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — union types](https://docs.python.org/3/library/stdtypes.html#union-type)

---CARD---

### Front

How do collection type annotations describe nested values?

```python
metrics: dict[str, float] = {
    "accuracy": 0.94,
    "loss": 0.12,
}
artifact_names: list[str] = ["model.pkl", "report.json"]
```

### Back

`dict[str, float]` means string keys mapped to float values. `list[str]` means a list whose elements should be strings. These annotations guide readers, editors, and type checkers.

```python
def best_metric(values: dict[str, float]) -> tuple[str, float]:
    return max(values.items(), key=lambda item: item[1])
```

**Application:** Typed collections make data-shape mistakes visible before integration tests or cloud jobs run.

**Card ID:** B024
**Tags:** typing, collections, annotations
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — typing](https://docs.python.org/3/library/typing.html)

---CARD---

### Front

Why can a function be passed as an argument?

```python
def normalize(name: str) -> str:
    return name.strip().lower()

def prepare(name: str, transform) -> str:
    return transform(name)
```

### Back

Functions are objects, so they can be stored and passed like other values. For a precise annotation, use `Callable`.

```python
from collections.abc import Callable

def prepare(name: str, transform: Callable[[str], str]) -> str:
    return transform(name)

result = prepare(" Model-A ", normalize)
```

**Application:** Passing behavior supports callbacks and simple dependency injection without requiring a class hierarchy.

**Card ID:** B025
**Tags:** functions, callable, callbacks
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python language reference — function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions)

---CARD---

### Front

What does a decorator do to a function?

```python
def announce(function):
    def wrapper():
        print("starting")
        return function()
    return wrapper

@announce
def train() -> None:
    print("training")
```

### Back

A decorator receives the defined function and replaces it with the returned object. Calling `train()` now calls `wrapper`, which adds behavior before delegating.

```python
# This is roughly what @announce means:
def train() -> None:
    print("training")

train = announce(train)
```

Production decorators should preserve metadata and signatures; the advanced deck covers `functools.wraps` and `ParamSpec`.

**Application:** Decorators suit cross-cutting behavior such as tracing, but can hide control flow if overused.

**Card ID:** B026
**Tags:** decorators, functions, wrappers
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python glossary — decorator](https://docs.python.org/3/glossary.html#term-decorator)

---CARD---

### Front

What makes this object iterable?

```python
artifact_names = ["model.pkl", "metrics.json"]
for name in artifact_names:
    print(name)
```

### Back

An iterable can produce an iterator. A `for` loop repeatedly asks that iterator for the next item until it is exhausted. Lists, tuples, dictionaries, files, and generators are iterable.

```python
iterator = iter(artifact_names)
print(next(iterator))
print(next(iterator))
```

**Application:** APIs that return iterables let callers stream, filter, or stop early instead of requiring a fully built list.

**Card ID:** B027
**Tags:** iterable, iterator, for-loop
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — iterators](https://docs.python.org/3/tutorial/classes.html#iterators)

---CARD---

### Front

How is a generator different from a list-returning function?

```python
def page_numbers(total: int):
    for number in range(1, total + 1):
        yield number
```

### Back

Because it uses `yield`, calling the function returns a generator. Values are produced lazily, one at a time, as the caller iterates.

```python
for page in page_numbers(3):
    print(page)
```

This can reduce memory use and allow early stopping. A list is simpler when the data is small and callers need repeated random access.

**Application:** Pagination and large artifact listings are natural generator use cases.

**Card ID:** B028
**Tags:** generators, yield, lazy-evaluation
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — generators](https://docs.python.org/3/tutorial/classes.html#generators)

---CARD---

### Front

What does `async def` change about this function?

```python
import asyncio

async def wait_for_job() -> str:
    await asyncio.sleep(0.1)
    return "done"
```

### Back

Calling an async function creates a coroutine; its body runs when it is awaited by an event loop. `await` lets other async tasks make progress while this task waits.

```python
async def main() -> None:
    result = await wait_for_job()
    print(result)

asyncio.run(main())
```

**Application:** Async I/O helps coordinate many waiting network operations. It does not automatically speed up CPU-heavy model computation.

**Card ID:** B029
**Tags:** async, await, coroutine
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python library reference — coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html)

---CARD---

### Front

Why is injecting the client easier to test than constructing it inside the function?

```python
def upload_report(report: bytes, client) -> None:
    client.upload("report.json", report)
```

### Back

The dependency is explicit, so production can pass a real client and tests can pass a small fake. The function stays focused on its policy.

```python
class FakeClient:
    def __init__(self) -> None:
        self.names: list[str] = []

    def upload(self, name: str, data: bytes) -> None:
        self.names.append(name)

fake = FakeClient()
upload_report(b"{}", fake)
assert fake.names == ["report.json"]
```

**Application:** This is dependency injection: a central idea in the advanced CLI and service-boundary cards.

**Card ID:** B030
**Tags:** dependency-injection, testing, fakes
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — classes](https://docs.python.org/3/tutorial/classes.html)

---CARD---

### Front

What should a basic unit test verify here?

```python
def model_uri(model: str, version: int) -> str:
    if version < 1:
        raise ValueError("version must be positive")
    return f"models:/{model}/{version}"
```

### Back

Test observable behavior: a representative success and an important failure. Avoid testing private implementation steps.

```python
import pytest

def test_model_uri() -> None:
    assert model_uri("fraud", 2) == "models:/fraud/2"

def test_model_uri_rejects_zero() -> None:
    with pytest.raises(ValueError):
        model_uri("fraud", 0)
```

**Application:** Fast unit tests give confidence in validation and domain rules without contacting MLflow or GCP.

**Card ID:** B031
**Tags:** testing, pytest, unit-tests
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [pytest documentation — getting started](https://docs.pytest.org/en/stable/getting-started.html)

---CARD---

### Front

Why should a Click command call an ordinary Python function?

```python
def deploy(model: str) -> str:
    return f"deployed {model}"

import click

@click.command()
@click.argument("model")
def deploy_command(model: str) -> None:
    click.echo(deploy(model))
```

### Back

Click handles command-line parsing and output, while `deploy` contains reusable behavior. Library callers and tests can call `deploy` without constructing a CLI context.

```python
def test_deploy_logic() -> None:
    assert deploy("fraud-v2") == "deployed fraud-v2"
```

**Application:** Think of a command as a thin adapter: parse input, call the package API, render the result, and translate known errors.

**Card ID:** B032
**Tags:** click, cli, library-api, separation
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Click documentation — commands and groups](https://click.palletsprojects.com/en/stable/commands/)

---CARD---

### Front

What is the difference between `print` and logging?

```python
import logging

logger = logging.getLogger(__name__)
logger.info("training started", extra={"run_id": "r-123"})
```

### Back

`print` writes text directly. Logging records an event with a level and metadata and can be routed, filtered, and formatted by application configuration.

```python
def train(run_id: str) -> None:
    logger.info("training started", extra={"run_id": run_id})
```

Never include tokens, passwords, or credential objects in either output.

**Application:** Libraries should log diagnostic events and return values or raise errors; CLI adapters decide what users see.

**Card ID:** B033
**Tags:** logging, print, observability
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)

---CARD---

### Front

What does `if __name__ == "__main__"` accomplish?

```python
def main() -> None:
    print("starting command")

if __name__ == "__main__":
    main()
```

### Back

The guarded code runs when the file is executed as a script, but not when it is imported as a module. This prevents accidental command execution during imports.

```python
# another_module.py
from command import main  # Defines main; does not call it.
```

**Application:** Installed packages normally expose CLI entry points through `pyproject.toml`, but the same principle remains: imports should define behavior, not start it.

**Card ID:** B034
**Tags:** modules, main-guard, cli
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python documentation — `__main__`](https://docs.python.org/3/library/__main__.html)

---CARD---

### Front

What is a public API in a Python package?

```python
# mlops_tools/__init__.py
from .deployments import deploy_model

__all__ = ["deploy_model"]
```

### Back

A public API is the supported set of names and behaviors callers are expected to use. Re-exporting selected functions can give users a stable, convenient import while internals evolve.

```python
from mlops_tools import deploy_model

result = deploy_model("fraud-v2")
```

`__all__` documents export intent for wildcard imports, but it does not make private code inaccessible.

**Application:** Keep public surfaces small and deliberate; changing them can break downstream callers.

**Card ID:** B035
**Tags:** packages, public-api, imports
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial — importing from a package](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package)

---CARD---

### Front

How should you progress from this deck to the advanced deck?

```python
def ready_for_advanced(concepts: set[str]) -> bool:
    prerequisites = {
        "functions", "classes", "exceptions",
        "iterators", "typing", "testing",
    }
    return prerequisites <= concepts
```

### Back

You do not need perfect recall. Move on when you can read the examples, predict straightforward results, and explain the highlighted vocabulary. Revisit prerequisite cards whenever an advanced card introduces too many unfamiliar ideas at once.

```python
study_order = [
    "python_basics_flashcards.md",
    "flashcards.md",
]
```

Recommended bridge topics are B021–B035: dataclasses, inheritance, typing, callables, decorators, iteration, generators, async, dependency injection, testing, CLI separation, and public APIs.

**Application:** Learning advanced Python works best as repeated passes: recognize a pattern first, then understand its tradeoffs, then apply it in a real package.

**Card ID:** B036
**Tags:** study-guide, prerequisites, advanced-python
**Difficulty:** Beginner
**Source type:** Official documentation
**Source:** [Python tutorial](https://docs.python.org/3/tutorial/)

---CARD---
