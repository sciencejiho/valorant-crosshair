import json
from pathlib import Path

import pytest


@pytest.fixture
def junior_code() -> str:
    fixture_path = Path(__file__).parents[1] / "examples" / "crosshairs.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return str(payload["junior_reference"]["code"])
