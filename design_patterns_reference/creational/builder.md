# Builder

## Plain-English idea

A builder holds an unfinished object while you add its parts one by one. It is
helpful when a normal constructor would have too many optional arguments or
when some choices are only valid together.

## Everyday worked example: plan a day out

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DayPlan:
    destination: str
    transport: str
    activities: tuple[str, ...]
    lunch_booked: bool


class DayPlanBuilder:
    def __init__(self) -> None:
        self.destination: str | None = None
        self.transport = "walk"
        self.activities: list[str] = []
        self.lunch_booked = False

    def visit(self, place: str) -> "DayPlanBuilder":
        self.destination = place
        return self

    def travel_by(self, transport: str) -> "DayPlanBuilder":
        self.transport = transport
        return self

    def add_activity(self, activity: str) -> "DayPlanBuilder":
        self.activities.append(activity)
        return self

    def book_lunch(self) -> "DayPlanBuilder":
        self.lunch_booked = True
        return self

    def build(self) -> DayPlan:
        if self.destination is None:
            raise ValueError("A destination is required")
        if not self.activities:
            raise ValueError("Choose at least one activity")
        return DayPlan(self.destination, self.transport, tuple(self.activities), self.lunch_booked)


plan = (
    DayPlanBuilder()
    .visit("City museum")
    .travel_by("train")
    .add_activity("Exhibition")
    .book_lunch()
    .build()
)
print(plan)
```

The builder is mutable while planning. The finished `DayPlan` is frozen, so it
cannot accidentally be changed after somebody relies on it.

## MLOps / SDK worked example: prepare a training request

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingRequest:
    image: str
    dataset: str
    arguments: tuple[str, ...]


class TrainingRequestBuilder:
    def __init__(self) -> None:
        self.image: str | None = None
        self.dataset: str | None = None
        self.arguments: list[str] = []

    def use_image(self, image: str) -> "TrainingRequestBuilder":
        self.image = image
        return self

    def use_dataset(self, dataset: str) -> "TrainingRequestBuilder":
        self.dataset = dataset
        return self

    def add_argument(self, argument: str) -> "TrainingRequestBuilder":
        self.arguments.append(argument)
        return self

    def build(self) -> TrainingRequest:
        if self.image is None or self.dataset is None:
            raise ValueError("image and dataset are required")
        return TrainingRequest(self.image, self.dataset, tuple(self.arguments))


request = (
    TrainingRequestBuilder()
    .use_image("trainer:2.0")
    .use_dataset("weekly.csv")
    .add_argument("--epochs=5")
    .build()
)
print(request)
```

## What problem does it solve?

The code that makes the object reads like the choices a person made. The
builder also has one final place to reject an incomplete request.

## When to use / not use it

Use it for genuinely multi-part construction. For a three-field value, a
dataclass with named arguments is almost always clearer. A builder introduces
another class and mutable intermediate state, so it should earn its place.

## Test it

Test that `build()` rejects each required missing part. Test that its result is
independent of later changes to the builder and that cross-field validation is
performed in one predictable place.
