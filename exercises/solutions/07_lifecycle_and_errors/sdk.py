from typing import Protocol


class SDKError(Exception):
    pass


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
        self._session = session

    def __enter__(self) -> "Upload":
        self._session.open()
        return self

    def send(self, payload: bytes) -> None:
        try:
            self._session.send(payload)
        except TransportError as error:
            if error.status == 401:
                raise AuthenticationError("authentication failed") from error
            raise

    def __exit__(self, *exc_info: object) -> None:
        self._session.close()

