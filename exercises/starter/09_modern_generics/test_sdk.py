"""Run with Python 3.12 or newer."""

from dataclasses import dataclass
import unittest

from sdk import Pager, index_by_id


@dataclass(frozen=True)
class Model:
    id: str
    version: int


class ModernGenericTests(unittest.TestCase):
    def test_pager_is_lazy_and_retains_decoded_type(self) -> None:
        calls: list[str | None] = []

        def fetch(cursor: str | None) -> dict[str, object]:
            calls.append(cursor)
            if cursor is None:
                return {"items": [{"id": "m1", "version": 1}], "next_cursor": "p2"}
            return {"items": [{"id": "m2", "version": 2}], "next_cursor": None}

        pager = Pager[Model](fetch, lambda row: Model(str(row["id"]), int(row["version"])))
        self.assertEqual(calls, [])
        models = list(pager)
        self.assertEqual([model.id for model in models], ["m1", "m2"])
        self.assertEqual(calls, [None, "p2"])

    def test_bounded_generic_preserves_concrete_values(self) -> None:
        model = Model("m1", 3)
        self.assertIs(index_by_id([model])["m1"], model)


if __name__ == "__main__":
    unittest.main()

