import json
import unittest

from sdk import MemoryBlobStore, Repository


class JsonCodec:
    def encode(self, value: object) -> bytes:
        return json.dumps(value).encode()

    def decode(self, value: bytes) -> object:
        return json.loads(value)


class RepositoryTests(unittest.TestCase):
    def test_round_trip_uses_injected_collaborators(self) -> None:
        store = MemoryBlobStore({})
        repository: Repository[dict[str, int]] = Repository(store, JsonCodec())
        repository.save("metrics", {"accuracy": 1})
        self.assertEqual(repository.get("metrics"), {"accuracy": 1})
        self.assertEqual(store.values["metrics"], b'{"accuracy": 1}')

    def test_store_contract_preserves_missing_key(self) -> None:
        with self.assertRaises(KeyError):
            MemoryBlobStore({}).read("missing")


if __name__ == "__main__":
    unittest.main()

