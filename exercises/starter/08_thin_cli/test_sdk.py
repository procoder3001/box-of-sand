from io import StringIO
import unittest

from sdk import DeploymentService, run_cli


class FakeGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def create(self, model: str, replicas: int) -> str:
        self.calls.append((model, replicas))
        return "dep-123"


class CliTests(unittest.TestCase):
    def test_library_api_is_independent_of_cli(self) -> None:
        gateway = FakeGateway()
        result = DeploymentService(gateway).deploy("fraud", 2)
        self.assertEqual(result, "dep-123")
        self.assertEqual(gateway.calls, [("fraud", 2)])

    def test_cli_is_a_thin_adapter(self) -> None:
        gateway = FakeGateway()
        out, err = StringIO(), StringIO()
        code = run_cli(["deploy", "fraud", "--replicas", "3"], DeploymentService(gateway), out, err)
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "deployed dep-123\n")
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(gateway.calls, [("fraud", 3)])

    def test_domain_error_becomes_friendly_stderr(self) -> None:
        gateway = FakeGateway()
        out, err = StringIO(), StringIO()
        code = run_cli(["deploy", "fraud", "--replicas", "0"], DeploymentService(gateway), out, err)
        self.assertEqual(code, 2)
        self.assertIn("replicas must be positive", err.getvalue())
        self.assertEqual(gateway.calls, [])

    def test_bad_syntax_does_not_call_service(self) -> None:
        gateway = FakeGateway()
        code = run_cli(["wrong"], DeploymentService(gateway), StringIO(), StringIO())
        self.assertEqual(code, 2)
        self.assertEqual(gateway.calls, [])


if __name__ == "__main__":
    unittest.main()

