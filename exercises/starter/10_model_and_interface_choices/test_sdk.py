import importlib.util
import unittest

PYDANTIC_AVAILABLE = importlib.util.find_spec("pydantic") is not None
if PYDANTIC_AVAILABLE:
    from pydantic import ValidationError
    from sdk import ArtifactStore, ModelArchiver, ModelRef, ModelsClient


@unittest.skipUnless(PYDANTIC_AVAILABLE, "install requirements.txt to run this exercise")
class ModelChoiceTests(unittest.TestCase):
    def test_external_payload_is_validated_then_becomes_value(self) -> None:
        class FakeTransport:
            def get(self, path: str) -> dict[str, object]:
                return {"name": "fraud", "version": 2}

        ref = ModelsClient(FakeTransport()).get("fraud")
        self.assertEqual(ref, ModelRef("fraud", 2))
        self.assertEqual(hash(ref), hash(ModelRef("fraud", 2)))

    def test_invalid_or_extra_external_fields_are_rejected(self) -> None:
        class BadTransport:
            def get(self, path: str) -> dict[str, object]:
                return {"name": "", "version": 0, "surprise": True}

        with self.assertRaises(ValidationError):
            ModelsClient(BadTransport()).get("fraud")

    def test_abc_supplies_policy_to_sdk_owned_implementation(self) -> None:
        class MemoryStore(ArtifactStore):
            def __init__(self) -> None:
                self.values: dict[str, bytes] = {}

            def save(self, key: str, content: bytes) -> None:
                self.values[key] = content

        store = MemoryStore()
        key = ModelArchiver(store).archive(ModelRef("fraud", 2), b"weights")
        self.assertEqual(key, "fraud/2/model.bin")
        self.assertEqual(store.values[key], b"weights")


if __name__ == "__main__":
    unittest.main()

