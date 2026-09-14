# Facade

## Plain-English idea

A facade gives callers one task-oriented operation over several lower-level
objects. The facade knows the needed sequence; callers do not have to memorize
or repeat it.

## Everyday worked example: check out a library book

```python
class MemberRegister:
    def is_active(self, member: str) -> bool:
        return member in {"Ava", "Noah"}


class BookShelf:
    def is_available(self, title: str) -> bool:
        return title != "Already borrowed"

    def lend(self, title: str, member: str) -> None:
        print(f"Loan recorded: {title} for {member}")


class ReminderService:
    def send_due_date(self, member: str, title: str) -> None:
        print(f"Message to {member}: return {title} in 3 weeks")


class LibraryDesk:
    def __init__(self, register: MemberRegister, shelf: BookShelf, reminders: ReminderService) -> None:
        self.register = register
        self.shelf = shelf
        self.reminders = reminders

    def check_out(self, member: str, title: str) -> None:
        if not self.register.is_active(member):
            raise ValueError("Membership is inactive")
        if not self.shelf.is_available(title):
            raise ValueError("Book is unavailable")
        self.shelf.lend(title, member)
        self.reminders.send_due_date(member, title)


desk = LibraryDesk(MemberRegister(), BookShelf(), ReminderService())
desk.check_out("Ava", "The Atlas")
```

The caller says “check out this book.” The facade owns validation, the order of
steps, and the common happy-path workflow.

## MLOps / SDK worked example: promote and deploy a model

```python
class ModelRegistry:
    def mark_ready(self, name: str, version: str) -> None:
        print(f"Registry: {name} {version} is ready")


class DeploymentClient:
    def create(self, name: str, version: str) -> str:
        deployment_id = f"deploy-{name}-{version}"
        print(f"Deployment started: {deployment_id}")
        return deployment_id


class ReleaseService:
    def __init__(self, registry: ModelRegistry, deployment: DeploymentClient) -> None:
        self.registry = registry
        self.deployment = deployment

    def publish(self, name: str, version: str) -> str:
        self.registry.mark_ready(name, version)
        return self.deployment.create(name, version)


release = ReleaseService(ModelRegistry(), DeploymentClient())
print(release.publish("recommendations", "v4"))
```

## What problem does it solve?

Facades create a friendly public API and stop multiple callers from duplicating
important workflow sequencing. A thin Click command should often call a facade
or service like this instead of coordinating SDK clients itself.

## When to use / not use it

Use one for a repeated, meaningful task. Do not create a vague all-purpose
`Manager`; that becomes a dumping ground. Keep lower-level services available
when callers genuinely need their individual capabilities.

## Test it

Inject fakes for each collaborator. Verify the order of calls, the returned
outcome, and what happens when a validation or external step fails.
