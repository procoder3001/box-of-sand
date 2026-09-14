# State

## Plain-English idea

State is useful when an object’s valid actions depend on where it is in a
lifecycle. Instead of placing every rule in one large `if` statement, each
state object handles the actions valid in that state.

## Everyday worked example: a library book’s loan lifecycle

```python
class OnShelf:
    def borrow(self, book: "LibraryBook", person: str) -> None:
        book.borrower = person
        book.state = OnLoan()
        print(f"{person} borrowed {book.title}")

    def return_book(self, book: "LibraryBook") -> None:
        raise ValueError("This book is already on the shelf")


class OnLoan:
    def borrow(self, book: "LibraryBook", person: str) -> None:
        raise ValueError(f"Already borrowed by {book.borrower}")

    def return_book(self, book: "LibraryBook") -> None:
        book.borrower = None
        book.state = OnShelf()
        print(f"{book.title} was returned")


class LibraryBook:
    def __init__(self, title: str) -> None:
        self.title = title
        self.borrower: str | None = None
        self.state: OnShelf | OnLoan = OnShelf()

    def borrow(self, person: str) -> None:
        self.state.borrow(self, person)

    def return_book(self) -> None:
        self.state.return_book(self)


book = LibraryBook("The Atlas")
book.borrow("Ava")
book.return_book()
```

The book delegates its actions to its current state. `OnLoan` owns the rule
that a second borrower is not allowed; `OnShelf` owns the opposite rule.

## MLOps / SDK worked example: lifecycle of a training job

```python
class Queued:
    def start(self, job: "TrainingJob") -> None:
        job.state = Running()
        print(f"Started {job.name}")

    def cancel(self, job: "TrainingJob") -> None:
        job.state = Cancelled()
        print(f"Cancelled queued job {job.name}")


class Running:
    def start(self, job: "TrainingJob") -> None:
        raise ValueError("Job is already running")

    def cancel(self, job: "TrainingJob") -> None:
        job.state = Cancelled()
        print(f"Requested cancellation for {job.name}")


class Cancelled:
    def start(self, job: "TrainingJob") -> None:
        raise ValueError("Cancelled jobs cannot start")

    def cancel(self, job: "TrainingJob") -> None:
        raise ValueError("Job is already cancelled")


class TrainingJob:
    def __init__(self, name: str) -> None:
        self.name = name
        self.state: Queued | Running | Cancelled = Queued()

    def start(self) -> None:
        self.state.start(self)

    def cancel(self) -> None:
        self.state.cancel(self)


job = TrainingJob("nightly-ranking")
job.start()
job.cancel()
```

## What problem does it solve?

It places each transition next to the state that permits or rejects it. As a
lifecycle grows, this can be clearer than repeating `if status == ...` across
many methods.

## When to use / not use it

For two states and one action, an enum plus an `if` is normally simpler. State
objects are worthwhile only when several actions have genuinely different rules
by state. They should not hide the transition diagram from readers.

## Test it

Write a transition table: starting state, action, result. Test valid changes
and every invalid action, including that invalid actions do not trigger an
external side effect.
