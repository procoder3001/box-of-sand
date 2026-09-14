# Observer

## Plain-English idea

Observer lets one object announce an event while other objects choose whether
to listen. The event source does not need to import or understand the details
of every listener.

## Everyday worked example: a school score board

```python
from collections.abc import Callable


ScoreListener = Callable[[str, int], None]


class ScoreBoard:
    def __init__(self) -> None:
        self.listeners: list[ScoreListener] = []
        self.score = 0

    def subscribe(self, listener: ScoreListener) -> None:
        self.listeners.append(listener)

    def unsubscribe(self, listener: ScoreListener) -> None:
        self.listeners.remove(listener)

    def add_points(self, team: str, points: int) -> None:
        self.score += points
        for listener in self.listeners:
            listener(team, self.score)


def update_screen(team: str, score: int) -> None:
    print(f"Screen: {team} now has {score} points")


def cheer(team: str, score: int) -> None:
    if score >= 10:
        print(f"Speaker: A cheer for {team}!")


board = ScoreBoard()
board.subscribe(update_screen)
board.subscribe(cheer)
board.add_points("Blue", 3)
board.add_points("Blue", 7)
board.unsubscribe(cheer)
board.add_points("Blue", 1)
```

`ScoreBoard` knows only that listeners accept a team and a score. It does not
need to be changed when a new listener, such as an online scoreboard, is added.

## MLOps / SDK worked example: react to a completed run

```python
from collections.abc import Callable


RunListener = Callable[[str, str], None]


class RunEvents:
    def __init__(self) -> None:
        self.listeners: list[RunListener] = []

    def subscribe(self, listener: RunListener) -> None:
        self.listeners.append(listener)

    def finished(self, run_id: str, status: str) -> None:
        for listener in self.listeners:
            listener(run_id, status)


def record_metrics(run_id: str, status: str) -> None:
    print(f"Metrics service records {run_id}: {status}")


def notify_owner(run_id: str, status: str) -> None:
    print(f"Message: run {run_id} ended with {status}")


events = RunEvents()
events.subscribe(record_metrics)
events.subscribe(notify_owner)
events.finished("run-17", "succeeded")
```

## What problem does it solve?

The producer stays loosely coupled to optional reactions. A run service can
announce completion without importing email, dashboards, or reporting code.

## When to use / not use it

Call one required action directly; observer is for independently optional
reactions. In-memory callbacks do not reliably deliver important work if the
process crashes. Use a durable queue or outbox when delivery must survive,
retry, or cross process boundaries.

## Test it

Use recording listener functions to assert the event payload, subscription,
and unsubscription behavior. Decide and test whether one listener’s exception
should stop the remaining listeners or be isolated.
