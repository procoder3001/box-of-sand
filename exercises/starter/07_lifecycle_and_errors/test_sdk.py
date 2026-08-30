import unittest

from sdk import AuthenticationError, TransportError, Upload


class FakeSession:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure
        self.events: list[str] = []

    def open(self) -> None:
        self.events.append("open")

    def send(self, payload: bytes) -> None:
        self.events.append("send")
        if self.failure:
            raise self.failure

    def close(self) -> None:
        self.events.append("close")


class LifecycleTests(unittest.TestCase):
    def test_closes_after_success(self) -> None:
        session = FakeSession()
        with Upload(session) as upload:
            upload.send(b"model")
        self.assertEqual(session.events, ["open", "send", "close"])

    def test_translates_auth_error_preserves_cause_and_closes(self) -> None:
        session = FakeSession(TransportError(401, "token expired"))
        with self.assertRaises(AuthenticationError) as raised:
            with Upload(session) as upload:
                upload.send(b"model")
        self.assertIsInstance(raised.exception.__cause__, TransportError)
        self.assertEqual(session.events, ["open", "send", "close"])

    def test_other_transport_errors_remain_unchanged(self) -> None:
        error = TransportError(503, "unavailable")
        with self.assertRaises(TransportError) as raised:
            with Upload(FakeSession(error)) as upload:
                upload.send(b"model")
        self.assertIs(raised.exception, error)


if __name__ == "__main__":
    unittest.main()

