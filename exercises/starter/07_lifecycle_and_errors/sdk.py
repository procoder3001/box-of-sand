"""Exercise 07: translate errors while guaranteeing cleanup."""

from typing import Protocol


class SDKError(Exception):
    """Base for errors callers may intentionally catch."""


class AuthenticationError(SDKError):
    pass


class TransportError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


class Session(Protocol):
    def open(self) -> None: ...
    def send(self, payload: bytes) -> None: ...
    def close(self) -> None: ...


class Upload:
    def __init__(self, session: Session) -> None:
        raise NotImplementedError

    def __enter__(self) -> "Upload":
        """Open the session and return self."""
        raise NotImplementedError

    def send(self, payload: bytes) -> None:
        """Translate a 401 TransportError to AuthenticationError using chaining."""
        raise NotImplementedError

    def __exit__(self, *exc_info: object) -> None:
        """Always close; never suppress an active exception."""
        raise NotImplementedError

