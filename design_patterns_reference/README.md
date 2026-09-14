# Practical Python Design Patterns

This folder is a compact, original reference for ten commonly named design
patterns. It is written for choosing a small, useful design in a Python
application—not for reproducing textbook class diagrams.

Each page begins with a complete, beginner-friendly everyday scenario. A
separate, complete MLOps/SDK scenario follows it so the translation does not
get in the way of learning the pattern. Every example is newly written and
independent of the research folder.

## Quick chooser

| If the problem is... | Start with... |
| --- | --- |
| Constructing an object depends on a runtime choice | [Factory](creational/factory.md) |
| A value has many optional, validated construction steps | [Builder](creational/builder.md) |
| A new object begins as a variation of an existing one | [Prototype](creational/prototype.md) |
| One process-wide resource needs a deliberate lifecycle | [Singleton](creational/singleton.md) |
| A dependency has the wrong interface | [Adapter](structural/adapter.md) |
| Independent behavior can be wrapped in layers | [Decorator](structural/decorator.md) |
| A frequent task coordinates several subsystems | [Facade](structural/facade.md) |
| An algorithm changes while the caller stays the same | [Strategy](behavioral/strategy.md) |
| Behavior changes with an object's current mode | [State](behavioral/state.md) |
| Interested parties react to an event | [Observer](behavioral/observer.md) |

## A Python-first rule

Begin with a function, a dataclass, or a dictionary. Introduce a named pattern
only once changing behavior, construction, or dependencies would otherwise
spread conditionals and coupling across multiple callers. Patterns are useful
vocabulary; they are not requirements.

## Layout

- `creational/` concerns how objects are made.
- `structural/` concerns how objects collaborate.
- `behavioral/` concerns how behavior is selected or communicated.

Run an example by copying its fenced Python code into a file and running
`python file.py`. The examples use only the standard library.
