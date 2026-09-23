# VALORANT Crosshair Lab

VALORANT Crosshair Lab is a Python 3.12+ project for parsing, inspecting,
converting, and experimentally matching VALORANT crosshair codes across
display resolutions.

The current release provides lossless parsing, structured diagnostics,
immutable parameter editing, exact serialization, and geometric resolution
conversion through a command-line interface.

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

## Convert a Crosshair

```powershell
.venv\Scripts\crosshair-lab.exe convert `
  --from 1920x1080 `
  --to 3840x2160 `
  "0;P;c;5;0t;1;0l;2;0v;2;0o;0"
```

Add `--json` for machine-readable output. Use `--policy` with `vertical`,
`horizontal`, `fit`, `fill`, or `custom`; custom scaling also requires
`--scale`. Rounding choices are `nearest`, `floor`, `ceil`, `preserve_odd`,
and `preserve_even`.

The converter scales only dimensional values already present under keys `t`,
`z`, `0t`, `0l`, `0v`, `0o`, `1t`, `1l`, `1v`, and `1o`. Unknown parameters
and omitted defaults are preserved. This is geometric conversion, not a claim
that VALORANT will rasterize the result identically; pixel previews and
raster-aware candidate search remain future work.
