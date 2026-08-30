import inspect
import unittest

from sdk import retry


class DecoratorTests(unittest.TestCase):
    def test_retries_only_selected_exception(self) -> None:
        calls = 0

        @retry(attempts=3, retry_on=(TimeoutError,))
        def fetch(name: str, *, limit: int = 1) -> str:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise TimeoutError("temporary")
            return name * limit

        self.assertEqual(fetch("m", limit=2), "mm")
        self.assertEqual(calls, 3)
        self.assertEqual(fetch.__name__, "fetch")
        self.assertEqual(str(inspect.signature(fetch)), "(name: str, *, limit: int = 1) -> str")

    def test_does_not_retry_permanent_failure(self) -> None:
        calls = 0

        @retry(attempts=3, retry_on=(TimeoutError,))
        def fail() -> None:
            nonlocal calls
            calls += 1
            raise ValueError("invalid")

        with self.assertRaises(ValueError):
            fail()
        self.assertEqual(calls, 1)

    def test_rejects_invalid_attempt_count(self) -> None:
        with self.assertRaises(ValueError):
            retry(attempts=0, retry_on=(TimeoutError,))


if __name__ == "__main__":
    unittest.main()

