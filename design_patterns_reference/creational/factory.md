# Factory

## Plain-English idea

A factory puts the decision about *which object to create* in one clear place.
The caller asks for a delivery method and then uses it; the caller does not
need a separate `if` statement every time it sends a package.

## Everyday worked example: a parcel counter

```python
from dataclasses import dataclass


@dataclass
class Parcel:
    address: str
    weight_kg: float


class BicycleDelivery:
    def deliver(self, parcel: Parcel) -> None:
        print(f"Bike courier takes {parcel.weight_kg}kg to {parcel.address}")


class VanDelivery:
    def deliver(self, parcel: Parcel) -> None:
        print(f"Van driver takes {parcel.weight_kg}kg to {parcel.address}")


class ParcelCounter:
    def choose_delivery(self, parcel: Parcel) -> BicycleDelivery | VanDelivery:
        if parcel.weight_kg <= 5:
            return BicycleDelivery()
        return VanDelivery()

    def send(self, parcel: Parcel) -> None:
        delivery_service = self.choose_delivery(parcel)
        delivery_service.deliver(parcel)


counter = ParcelCounter()
counter.send(Parcel("18 Oak Street", 2.4))
counter.send(Parcel("6 River Road", 12.0))
```

`choose_delivery()` is the factory method. It owns the “light parcel versus
heavy parcel” construction rule. `send()` only cares that the chosen object
has a `deliver()` method.

## MLOps / SDK worked example: choose artifact storage from a URI

```python
from dataclasses import dataclass


class LocalStore:
    def __init__(self, root: str) -> None:
        self.root = root

    def save(self, filename: str) -> None:
        print(f"Saved {filename} below {self.root}")


class CloudStore:
    def __init__(self, bucket_uri: str) -> None:
        self.bucket_uri = bucket_uri

    def save(self, filename: str) -> None:
        print(f"Uploaded {filename} to {self.bucket_uri}")


@dataclass
class ArtifactSettings:
    location: str


def make_artifact_store(settings: ArtifactSettings) -> LocalStore | CloudStore:
    if settings.location.startswith("gs://"):
        return CloudStore(settings.location)
    return LocalStore(settings.location)


store = make_artifact_store(ArtifactSettings("gs://demo-artifacts"))
store.save("evaluation.json")
```

## What problem does it solve?

Without the factory, every CLI command and service might decide which storage
class to create. A new storage option would then require hunting through those
callers. The factory gives that decision one home.

## When to use / not use it

Use a factory when a setting, identifier, or input selects one of several
implementations. For one concrete class, just call its constructor. A factory
should make object creation easier to find—not become a sprawling registry for
two choices.

## Test it

Test each selection rule: a light parcel gets a bike and a heavy parcel gets a
van. Separately, pass a tiny fake delivery service to any business logic that
needs to be tested without real delivery or cloud storage.
