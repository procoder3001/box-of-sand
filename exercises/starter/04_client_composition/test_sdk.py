import unittest

from sdk import SDKClient


class FakeTransport:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, object]] = []
        self.closed = False

    def request(self, method: str, path: str, *, json: dict[str, object] | None = None) -> dict[str, object]:
        self.requests.append((method, path, json))
        return {"name": path.rsplit("/", 1)[-1], "version": 7}

    def close(self) -> None:
        self.closed = True


class ClientTests(unittest.TestCase):
    def test_resource_is_lazy_cached_and_maps_response(self) -> None:
        transport = FakeTransport()
        client = SDKClient(transport)
        self.assertIs(client.models, client.models)
        model = client.models.get("fraud")
        self.assertEqual((model.name, model.version), ("fraud", 7))
        self.assertEqual(transport.requests, [("GET", "/models/fraud", None)])

    def test_context_manager_closes_owned_session_boundary(self) -> None:
        transport = FakeTransport()
        with SDKClient(transport) as client:
            self.assertIsInstance(client, SDKClient)
        self.assertTrue(transport.closed)


if __name__ == "__main__":
    unittest.main()

