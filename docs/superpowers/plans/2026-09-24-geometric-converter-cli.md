# Geometric Converter and CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a tested, installable command-line tool that converts present dimensional VALORANT crosshair parameters between screen resolutions and explains every change.

**Architecture:** Add immutable resolution and conversion-result models, a centralized parameter registry, deterministic Decimal-based scale and rounding policies, and a converter that rebuilds the ordered token stream without losing unknown data. Expose the workflow through an argparse CLI with text and JSON reports; keep all policy in the core.

**Tech Stack:** Python 3.12+, standard-library Decimal/dataclasses/enums/argparse/json, pytest 8, uv.

**Spec:** `valorant_crosshair_lab_SPEC.md` (sections 4–11, 19, 20–24, and Milestones 2–3)

## Global Constraints

- Scale only dimensional parameters present in the input; minimal serialization must not invent omitted defaults.
- Preserve unknown parameters, ordering, duplicates, sections, and trailing delimiter behavior.
- Use Decimal for numeric parsing, scale factors, ideal values, and outputs; do not use binary float arithmetic.
- Default to vertical scaling and nearest integer rounding; expose every alternative explicitly.
- Reject non-positive resolutions and custom scales; warn and preserve invalid or negative scalable values.
- Keep the converter and registry independent of CLI, TUI, GUI, and raster code.
- Bound CLI input through the existing parser limits and never access the game process or files.

## Review Focus

- Mismatched aspect ratios must emit a warning that names horizontal and vertical factors (Task 3).
- Half values must round deterministically rather than use Python's banker rounding (Task 2).
- Invalid numeric values on scalable keys must remain unchanged and appear in warnings (Task 3).
- Duplicate scalable keys must each be converted in their original positions (Task 3).
- CLI JSON must be machine-readable with no explanatory text mixed into stdout (Task 4).

---

### Task 1: Resolution Model and Parameter Registry

**Files:**
- Create: `src/crosshair_lab/resolution.py`
- Create: `src/crosshair_lab/parameters.py`
- Create: `tests/test_resolution.py`
- Create: `tests/test_parameters.py`

**Interfaces:**
- Produces: `Resolution(width: int, height: int)`, `parse_resolution(text: str) -> Resolution`, `ParameterSpec`, `PARAMETERS`, and `scalable_parameter(key: str) -> ParameterSpec | None`.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_resolution.py
import pytest
from crosshair_lab.resolution import Resolution, parse_resolution

def test_parse_resolution_accepts_lower_and_upper_x() -> None:
    assert parse_resolution("1920x1080") == Resolution(1920, 1080)
    assert parse_resolution("3840X2160") == Resolution(3840, 2160)

@pytest.mark.parametrize("text", ["", "1920", "0x1080", "-1x1080", "axb"])
def test_parse_resolution_rejects_invalid_values(text: str) -> None:
    with pytest.raises(ValueError):
        parse_resolution(text)

def test_resolution_exposes_exact_decimal_scale_factors() -> None:
    source = Resolution(2560, 1440)
    target = Resolution(3840, 2160)
    assert source.horizontal_scale_to(target).as_integer_ratio() == (3, 2)
    assert source.vertical_scale_to(target).as_integer_ratio() == (3, 2)
```

```python
# tests/test_parameters.py
from crosshair_lab.parameters import scalable_parameter

def test_registry_marks_supported_dimensions_as_scalable() -> None:
    for key in ("t", "z", "0t", "0l", "0v", "0o", "1t", "1l", "1v", "1o"):
        spec = scalable_parameter(key)
        assert spec is not None
        assert spec.scalable

def test_registry_does_not_scale_opacity_or_unknown_keys() -> None:
    assert scalable_parameter("0a") is None
    assert scalable_parameter("xyz") is None
```

- [ ] **Step 2: Verify red**

Run `.venv\Scripts\python.exe -m pytest tests/test_resolution.py tests/test_parameters.py -v`.

Expected: collection fails because both modules are absent.

- [ ] **Step 3: Implement the exact interfaces**

Use frozen, slotted dataclasses. `Resolution.__post_init__` raises `ValueError` unless both dimensions are positive integers. Parsing accepts exactly `<digits>x<digits>` case-insensitively. Scale methods return Decimal division.

`ParameterSpec` contains `key`, `name`, and `scalable`. Register the ten keys from the test with human-readable names; return only scalable specs from `scalable_parameter`.

- [ ] **Step 4: Verify green and commit**

Run the focused tests, then the full suite. Commit as `Add resolution model and parameter registry`.

### Task 2: Scale and Rounding Policies

**Files:**
- Create: `src/crosshair_lab/policies.py`
- Create: `tests/test_policies.py`

**Interfaces:**
- Produces: `ScalePolicy`, `RoundingPolicy`, `calculate_scale(source, target, policy, custom_scale=None) -> Decimal`, and `round_dimension(value, policy) -> Decimal`.

- [ ] **Step 1: Write failing policy tests**

```python
from decimal import Decimal
import pytest
from crosshair_lab.policies import (
    RoundingPolicy, ScalePolicy, calculate_scale, round_dimension,
)
from crosshair_lab.resolution import Resolution

SOURCE = Resolution(1920, 1080)
TARGET = Resolution(2560, 1440)

def test_scale_policies_are_explicit() -> None:
    assert calculate_scale(SOURCE, TARGET, ScalePolicy.VERTICAL) == Decimal("1.333333333333333333333333333")
    assert calculate_scale(SOURCE, TARGET, ScalePolicy.HORIZONTAL) == Decimal("1.333333333333333333333333333")
    assert calculate_scale(SOURCE, Resolution(2560, 1080), ScalePolicy.FIT) == Decimal("1")
    assert calculate_scale(SOURCE, Resolution(2560, 1080), ScalePolicy.FILL) == Decimal("1.333333333333333333333333333")

def test_custom_scale_requires_positive_value() -> None:
    assert calculate_scale(SOURCE, TARGET, ScalePolicy.CUSTOM, Decimal("1.25")) == Decimal("1.25")
    with pytest.raises(ValueError):
        calculate_scale(SOURCE, TARGET, ScalePolicy.CUSTOM)
    with pytest.raises(ValueError):
        calculate_scale(SOURCE, TARGET, ScalePolicy.CUSTOM, Decimal("0"))

@pytest.mark.parametrize(
    ("policy", "expected"),
    [
        (RoundingPolicy.NEAREST, Decimal("2")),
        (RoundingPolicy.FLOOR, Decimal("1")),
        (RoundingPolicy.CEIL, Decimal("2")),
        (RoundingPolicy.PRESERVE_ODD, Decimal("1")),
        (RoundingPolicy.PRESERVE_EVEN, Decimal("2")),
    ],
)
def test_rounding_policies_handle_half_deterministically(policy, expected) -> None:
    assert round_dimension(Decimal("1.5"), policy) == expected
```

- [ ] **Step 2: Verify red**

Run `.venv\Scripts\python.exe -m pytest tests/test_policies.py -v`.

Expected: collection fails because `crosshair_lab.policies` is absent.

- [ ] **Step 3: Implement policies**

Use string enums with values `vertical`, `horizontal`, `fit`, `fill`, `custom` and `nearest`, `floor`, `ceil`, `preserve_odd`, `preserve_even`. Nearest uses `ROUND_HALF_UP`. Parity modes choose the closest non-negative integer with the requested parity, resolving equal distance toward the smaller integer.

- [ ] **Step 4: Verify green and commit**

Run focused tests and the full suite. Commit as `Add scale and rounding policies`.

### Task 3: Geometric Conversion Engine

**Files:**
- Create: `src/crosshair_lab/conversion/__init__.py`
- Create: `src/crosshair_lab/conversion/geometric.py`
- Create: `tests/test_geometric_conversion.py`
- Modify: `src/crosshair_lab/__init__.py`

**Interfaces:**
- Produces: `ParameterChange`, `ConversionResult`, and `convert_geometric(code, source_resolution, target_resolution, *, scale_policy=VERTICAL, rounding_policy=NEAREST, custom_scale=None) -> ConversionResult`.

- [ ] **Step 1: Write failing conversion tests**

```python
from decimal import Decimal
from crosshair_lab import parse_crosshair, serialize_crosshair
from crosshair_lab.conversion import convert_geometric
from crosshair_lab.policies import RoundingPolicy, ScalePolicy
from crosshair_lab.resolution import Resolution

def parsed(text: str):
    result = parse_crosshair(text)
    assert result.code is not None
    return result.code

def test_1080p_to_4k_scales_present_dimensions_and_preserves_other_data() -> None:
    source = parsed("0;P;c;5;0t;1;0l;2;0v;2;0o;0;xyz;7;S;c;5")
    result = convert_geometric(source, Resolution(1920,1080), Resolution(3840,2160))
    assert result.scale_factor == Decimal("2")
    assert serialize_crosshair(result.converted) == "0;P;c;5;0t;2;0l;4;0v;4;0o;0;xyz;7;S;c;5"
    assert [(c.key, c.old_value, c.output_value) for c in result.changes] == [
        ("0t", Decimal("1"), Decimal("2")),
        ("0l", Decimal("2"), Decimal("4")),
        ("0v", Decimal("2"), Decimal("4")),
        ("0o", Decimal("0"), Decimal("0")),
    ]

def test_1440p_to_4k_uses_requested_rounding() -> None:
    result = convert_geometric(
        parsed("0;P;0t;1;0l;2"),
        Resolution(2560,1440),
        Resolution(3840,2160),
        rounding_policy=RoundingPolicy.FLOOR,
    )
    assert serialize_crosshair(result.converted) == "0;P;0t;1;0l;3"

def test_invalid_scalable_value_is_preserved_with_warning() -> None:
    result = convert_geometric(
        parsed("0;P;0t;thin;0l;-2"),
        Resolution(1920,1080),
        Resolution(3840,2160),
    )
    assert serialize_crosshair(result.converted) == "0;P;0t;thin;0l;-2"
    assert len(result.warnings) == 2

def test_mismatched_aspect_ratio_warns_and_duplicate_keys_both_convert() -> None:
    result = convert_geometric(
        parsed("0;P;0l;1;0l;2"),
        Resolution(1920,1080),
        Resolution(2560,1080),
        scale_policy=ScalePolicy.VERTICAL,
    )
    assert serialize_crosshair(result.converted) == "0;P;0l;1;0l;2"
    assert any("aspect ratio" in warning for warning in result.warnings)
```

- [ ] **Step 2: Verify red**

Run `.venv\Scripts\python.exe -m pytest tests/test_geometric_conversion.py -v`.

Expected: collection fails because the conversion package is absent.

- [ ] **Step 3: Implement immutable results and ordered conversion**

`ParameterChange` records section, key, old, ideal, output, and reason. `ConversionResult` records source/converted models, resolutions, policies, factor, changes, and warnings. Iterate the bounded element tuple, replace each valid non-negative scalable Decimal, format integral outputs without a decimal suffix, and leave every other element untouched.

- [ ] **Step 4: Export, verify, and commit**

Export conversion, policy, registry, and resolution symbols from the package root. Run focused tests and the full suite. Commit as `Add geometric resolution conversion`.

### Task 4: Converter CLI and Documentation

**Files:**
- Create: `src/crosshair_lab/cli.py`
- Create: `tests/test_cli.py`
- Modify: `pyproject.toml`
- Modify: `README.md`

**Interfaces:**
- Produces: `main(argv: Sequence[str] | None = None) -> int` and the `crosshair-lab` console command.

- [ ] **Step 1: Write failing CLI tests**

```python
import json
from crosshair_lab.cli import main

CODE = "0;P;c;5;0t;1;0l;2;0v;2;0o;0"

def test_convert_command_prints_result_and_change_table(capsys) -> None:
    exit_code = main(["convert", "--from", "1920x1080", "--to", "3840x2160", CODE])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Scale factor: 2" in output
    assert "0l: 2 -> 4" in output
    assert "0;P;c;5;0t;2;0l;4;0v;4;0o;0" in output

def test_convert_json_is_machine_readable(capsys) -> None:
    exit_code = main(["convert", "--json", "--from", "1920x1080", "--to", "3840x2160", CODE])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["scale_factor"] == "2"
    assert payload["result_code"].endswith("0o;0")

def test_invalid_crosshair_reports_stderr_and_nonzero(capsys) -> None:
    exit_code = main(["convert", "--from", "1920x1080", "--to", "4kx2160", "0;s"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "error:" in captured.err.lower()
```

- [ ] **Step 2: Verify red**

Run `.venv\Scripts\python.exe -m pytest tests/test_cli.py -v`.

Expected: collection fails because `crosshair_lab.cli` is absent.

- [ ] **Step 3: Implement CLI and entry point**

Add `[project.scripts] crosshair-lab = "crosshair_lab.cli:main"`. Build an argparse `convert` subcommand with `--from`, `--to`, `--policy`, `--round`, `--scale`, and `--json`. Catch user-input `ValueError`, print one `error:` line to stderr, and return 2. Text output lists resolutions, policy, factor, warnings, changes, and final code. JSON stringifies Decimal and enum values.

- [ ] **Step 4: Document and verify end to end**

Update README with installation and text/JSON examples, limitations, and the supported scalable keys. Run focused/full tests, reinstall editable metadata, and invoke:

```powershell
.venv\Scripts\crosshair-lab.exe convert --from 1920x1080 --to 3840x2160 "0;P;0t;1;0l;2"
```

Expected: exit 0 and result code `0;P;0t;2;0l;4`.

- [ ] **Step 5: Commit**

Commit as `Add geometric converter CLI`.

## Completion Criteria

- Editable install exposes `crosshair-lab`.
- Full pytest suite is green.
- 1080p→4K converts present dimensional values at factor 2 and preserves all other tokens.
- 1440p→4K honors the selected rounding policy.
- Aspect mismatch, invalid numeric dimensions, and negative dimensions are transparent warnings.
- Text and JSON CLI outputs both provide a copyable result code.
