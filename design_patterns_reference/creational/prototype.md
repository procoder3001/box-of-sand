# Prototype

## Plain-English idea

Prototype means starting with a useful existing value and making a variation of
it. In Python, an immutable dataclass plus `dataclasses.replace` often explains
the idea more plainly than writing a custom `clone()` method.

## Everyday worked example: reuse a club-event template

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ClubEvent:
    title: str
    room: str
    starts_at: str
    supplies: tuple[str, ...]

    def announcement(self) -> str:
        items = ", ".join(self.supplies)
        return f"{self.title} in {self.room}, {self.starts_at}. Bring: {items}"


weekly_craft = ClubEvent(
    title="Craft club",
    room="Room 4",
    starts_at="Wednesday 18:00",
    supplies=("scissors", "paper"),
)

holiday_craft = replace(
    weekly_craft,
    title="Holiday craft club",
    supplies=weekly_craft.supplies + ("glitter",),
)

print(weekly_craft.announcement())
print(holiday_craft.announcement())
```

`weekly_craft` is the prototype. The holiday event inherits its useful defaults
but is a separate value. The original tuple is never changed.

## MLOps / SDK worked example: create a quick validation run

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RunSettings:
    dataset_uri: str
    machine: str
    epochs: int
    tags: tuple[str, ...]


full_training = RunSettings(
    dataset_uri="datasets/monthly.csv",
    machine="standard-8",
    epochs=20,
    tags=("release-candidate",),
)

smoke_test = replace(
    full_training,
    dataset_uri="datasets/tiny.csv",
    epochs=1,
    tags=full_training.tags + ("smoke-test",),
)

print(full_training)
print(smoke_test)
```

## What problem does it solve?

It preserves a known-good starting point and makes the differences visible.
That is particularly useful for related configurations where rewriting every
field would make reviews harder.

## When to use / not use it

Use it when most fields remain the same. If most fields differ, make a new
object directly. Be especially careful with nested lists and dictionaries:
you must decide whether the old and new values should share them.

## Test it

Assert that the original object did not change and that the variation has only
the intended differences. For mutable nested data, write a test that proves
the copy behavior you want rather than assuming `copy` does it for you.
