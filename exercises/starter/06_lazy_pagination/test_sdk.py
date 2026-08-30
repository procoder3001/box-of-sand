import unittest

from sdk import ModelPager, Page


class PaginationTests(unittest.TestCase):
    def test_is_lazy_and_stops_fetching_when_consumer_stops(self) -> None:
        calls: list[str | None] = []

        def fetch(cursor: str | None) -> Page[str]:
            calls.append(cursor)
            return Page(["a", "b"], "next") if cursor is None else Page(["c"], None)

        pager = ModelPager(fetch)
        self.assertEqual(calls, [])
        iterator = iter(pager)
        self.assertEqual(next(iterator), "a")
        self.assertEqual(calls, [None])

    def test_follows_cursor_and_can_be_iterated_again(self) -> None:
        calls: list[str | None] = []

        def fetch(cursor: str | None) -> Page[str]:
            calls.append(cursor)
            return Page(["a", "b"], "next") if cursor is None else Page(["c"], None)

        pager = ModelPager(fetch)
        self.assertEqual(list(pager), ["a", "b", "c"])
        self.assertEqual(list(pager), ["a", "b", "c"])
        self.assertEqual(calls, [None, "next", None, "next"])


if __name__ == "__main__":
    unittest.main()

