# Singleton

## Plain-English idea

A singleton is one object shared by the relevant part of an application. In
Python, prefer making that sharing obvious: create it once at startup and pass
it to the objects that use it. The goal is shared ownership, not clever rules
that forbid a second constructor call.

## Everyday worked example: one music player for two rooms

```python
class MusicPlayer:
    def __init__(self) -> None:
        self.current_song: str | None = None
        self.volume = 5

    def play(self, song: str) -> None:
        self.current_song = song
        print(f"Now playing: {song}")

    def set_volume(self, volume: int) -> None:
        self.volume = volume


class RoomControl:
    def __init__(self, room_name: str, player: MusicPlayer) -> None:
        self.room_name = room_name
        self.player = player

    def play_music(self, song: str) -> None:
        print(f"{self.room_name} chooses a song")
        self.player.play(song)


shared_player = MusicPlayer()  # The application's one player.
kitchen = RoomControl("Kitchen", shared_player)
living_room = RoomControl("Living room", shared_player)

kitchen.play_music("Blue Sky")
living_room.player.set_volume(2)
print(shared_player.current_song, shared_player.volume)
```

There is one player because the program created one and injected the same
object into both controls. Nothing mysterious hides where that shared state is.

## MLOps / SDK worked example: create one client in the CLI entry point

```python
class ExperimentClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def log_metric(self, name: str, value: float) -> None:
        print(f"{self.endpoint}: {name}={value}")


class TrainingService:
    def __init__(self, client: ExperimentClient) -> None:
        self.client = client

    def record_accuracy(self, value: float) -> None:
        self.client.log_metric("accuracy", value)


def create_application() -> TrainingService:
    client = ExperimentClient("https://tracking.example")
    return TrainingService(client)


service = create_application()
service.record_accuracy(0.91)
```

## What problem does it solve?

Some things genuinely benefit from one owner: a connection pool, a metrics
exporter, or an immutable configuration. Creating it in an application
composition root makes startup and cleanup accountable.

## When to use / not use it

Do not make every service a singleton. Shared mutable globals make tests affect
each other and make multiple configurations in one process difficult. Also do
not open network clients or load credentials at import time.

## Test it

Create a fresh client in each test fixture and inject it into a service. Test
application startup and shutdown explicitly instead of relying on a global
singleton reset between tests.
