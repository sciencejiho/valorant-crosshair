# VALORANT Crosshair Lab

VALORANT Crosshair Lab is a Python 3.12+ project for parsing, inspecting,
converting, and experimentally matching VALORANT crosshair codes across
display resolutions.

The current foundation provides lossless parsing, structured diagnostics,
immutable parameter editing, and exact serialization. Conversion, previews,
and user interfaces are the next project slices.

## Development

```powershell
uv venv --python 3.14 .venv
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
.venv\Scripts\python.exe -m pytest
```

## Library Example

```python
from crosshair_lab import parse_crosshair, replace_parameter
from crosshair_lab import serialize_crosshair

result = parse_crosshair("0;P;c;5;0l;2")
if result.code is None:
    raise ValueError(result.errors)

edited = replace_parameter(
    result.code,
    key="0l",
    value="4",
    section="P",
)
print(serialize_crosshair(edited))
```

See `valorant_crosshair_lab_SPEC.md` for the architecture and roadmap.
