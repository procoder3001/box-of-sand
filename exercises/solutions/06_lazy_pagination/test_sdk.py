"""Run the shared behavioral tests against this reference implementation."""
from pathlib import Path
import runpy

globals().update({key: value for key, value in runpy.run_path(Path(__file__).parents[2] / "starter" / Path(__file__).parent.name / "test_sdk.py").items() if not key.startswith("__")})
