# Decorator

## Plain-English idea

An object decorator wraps another object and adds one feature while preserving
the same basic operation. It avoids making a subclass for every possible
combination of optional features.

## Everyday worked example: customise a cinema ticket

```python
class Ticket:
    def price(self) -> float:
        return 12.00

    def description(self) -> str:
        return "Cinema ticket"


class SnackBundle:
    def __init__(self, ticket: Ticket) -> None:
        self.ticket = ticket

    def price(self) -> float:
        return self.ticket.price() + 6.50

    def description(self) -> str:
        return self.ticket.description() + " + popcorn and drink"


class PremiumSeat:
    def __init__(self, ticket: Ticket | SnackBundle) -> None:
        self.ticket = ticket

    def price(self) -> float:
        return self.ticket.price() + 4.00

    def description(self) -> str:
        return self.ticket.description() + " + premium seat"


basic = Ticket()
family_treat = PremiumSeat(SnackBundle(basic))

print(basic.description(), basic.price())
print(family_treat.description(), family_treat.price())
```

`SnackBundle` and `PremiumSeat` can both answer `price()` and `description()`.
They add their own contribution, then delegate the rest to the wrapped ticket.

## MLOps / SDK worked example: add logging around a model uploader

```python
class ModelUploader:
    def upload(self, filename: str, destination: str) -> None:
        print(f"Uploaded {filename} to {destination}")


class LoggedUploader:
    def __init__(self, uploader: ModelUploader) -> None:
        self.uploader = uploader

    def upload(self, filename: str, destination: str) -> None:
        print(f"Starting upload: {filename}")
        self.uploader.upload(filename, destination)
        print("Upload complete")


class MetricsUploader:
    def __init__(self, uploader: LoggedUploader) -> None:
        self.uploader = uploader

    def upload(self, filename: str, destination: str) -> None:
        self.uploader.upload(filename, destination)
        print("Metric: model_uploads += 1")


uploader = MetricsUploader(LoggedUploader(ModelUploader()))
uploader.upload("model.pkl", "models/recommender")
```

## What problem does it solve?

The base object remains focused on its main job. Optional concerns—logging,
metrics, caching, retrying, authorization—can be assembled at application
startup instead of being baked into every implementation.

## When to use / not use it

Use decorators when enhancements are independent and can be combined in
different ways. A direct log statement is clearer for one operation. Avoid a
deep, undocumented wrapper stack: wrapper order can change behavior.

## Test it

Use a recording fake as the wrapped object. Assert that the decorator delegates
once, adds its own behavior, and preserves errors correctly. Test the few
wrapper combinations your application actually supports.
