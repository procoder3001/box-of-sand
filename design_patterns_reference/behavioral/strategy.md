# Strategy

## Plain-English idea

Strategy means selecting one of several ways to perform the same job. The main
workflow receives the chosen policy and uses it without knowing its details.
In Python, a function is often the simplest strategy object.

## Everyday worked example: choose a delivery-price rule

```python
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Order:
    total: float
    weight_kg: float


DeliveryRule = Callable[[Order], float]


def flat_rate(order: Order) -> float:
    return 5.00


def weight_based(order: Order) -> float:
    return 2.00 + 1.50 * order.weight_kg


def free_over_fifty(order: Order) -> float:
    if order.total >= 50:
        return 0.00
    return weight_based(order)


class Checkout:
    def __init__(self, delivery_rule: DeliveryRule) -> None:
        self.delivery_rule = delivery_rule

    def total_to_pay(self, order: Order) -> float:
        return order.total + self.delivery_rule(order)


order = Order(total=60, weight_kg=3)
print(Checkout(free_over_fifty).total_to_pay(order))
print(Checkout(weight_based).total_to_pay(order))
```

`Checkout` does not need an `if` branch for every pricing policy. Replacing the
function changes the rule while leaving checkout behavior intact.

## MLOps / SDK worked example: choose the rule for selecting a model

```python
from collections.abc import Callable


Candidate = dict[str, float]
SelectionRule = Callable[[Candidate], float]


def highest_accuracy(candidate: Candidate) -> float:
    return candidate["accuracy"]


def balanced_quality(candidate: Candidate) -> float:
    return 0.7 * candidate["accuracy"] + 0.3 * candidate["recall"]


class ModelSelector:
    def __init__(self, rule: SelectionRule) -> None:
        self.rule = rule

    def choose(self, candidates: list[Candidate]) -> Candidate:
        return max(candidates, key=self.rule)


models = [{"accuracy": 0.92, "recall": 0.61}, {"accuracy": 0.89, "recall": 0.84}]
print(ModelSelector(balanced_quality).choose(models))
```

## What problem does it solve?

Strategy separates “the work we always do” from “the policy we chose today.”
It keeps policy changes from turning one function into a growing list of
conditionals and makes experiments easier to express.

## When to use / not use it

Use it when two or more policies are real alternatives. One small conditional
is clearer than an elaborate strategy hierarchy. Start with functions; use
classes only when each strategy needs its own configuration or several methods.

## Test it

Test each rule with examples that make its decision obvious. Test the caller
with a tiny fake rule, such as `lambda _: 0`, to prove it actually delegates.
