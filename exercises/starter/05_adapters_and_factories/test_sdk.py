import unittest

from sdk import ArtifactStore, MemoryStore, store_for


class AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        MemoryStore.values = {"model": b"weights"}

    def test_subclass_registration_drives_factory(self) -> None:
        store = store_for("mem://model")
        self.assertIsInstance(store, MemoryStore)
        self.assertEqual(store.load("model"), b"weights")

    def test_unknown_and_duplicate_schemes_fail_early(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown artifact scheme"):
            store_for("gcs://bucket/model")
        with self.assertRaisesRegex(ValueError, "already registered"):
            class Duplicate(ArtifactStore, scheme="mem"):
                def load(self, location: str) -> bytes:
                    return b""

    def test_abstract_base_is_not_registered(self) -> None:
        self.assertEqual(ArtifactStore.registry, {"mem": MemoryStore})


if __name__ == "__main__":
    unittest.main()

