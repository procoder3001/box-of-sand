import unittest
from dataclasses import FrozenInstanceError

from sdk import ArtifactRef, ClientConfig


class ValueObjectTests(unittest.TestCase):
    def test_artifact_is_hashable_frozen_and_formats_uri(self) -> None:
        ref = ArtifactRef("models", "/run/model.pkl")
        self.assertEqual(ref.uri, "gs://models/run/model.pkl")
        self.assertEqual({ref}, {ArtifactRef("models", "/run/model.pkl")})
        with self.assertRaises(FrozenInstanceError):
            ref.path = "changed"  # type: ignore[misc]

    def test_config_validates_and_owns_header_default(self) -> None:
        first = ClientConfig("https://api.example.test/", 2)
        second = ClientConfig("https://api.example.test", 3)
        first.headers["x-run"] = "r1"
        self.assertEqual(first.endpoint, "https://api.example.test")
        self.assertEqual(second.headers, {})
        with self.assertRaises(ValueError):
            ClientConfig("https://api.example.test", 0)

    def test_from_mapping_converts_values(self) -> None:
        config = ClientConfig.from_mapping({"endpoint": "https://x.test/", "timeout": "4.5"})
        self.assertEqual(config, ClientConfig("https://x.test", 4.5))


if __name__ == "__main__":
    unittest.main()

