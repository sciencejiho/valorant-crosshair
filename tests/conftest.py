"""Shared regression fixtures for the test suite."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def junior_code() -> str:
    """Return the JUNiOR crosshair code from the example catalog."""
    fixture_path = Path(__file__).parents[1] / "examples" / "crosshairs.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return str(payload["junior_reference"]["code"])
